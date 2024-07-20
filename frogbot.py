import os
import random
import requests
import aiohttp
import discord
from discord.ext import commands, tasks
from discord import app_commands
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import json

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

CHANNEL_IDS_FILE = 'channel_ids.json'

# this checks the already stored channel IDs in the JSON file, so if a restart happens, the bot will remember the channel IDs
def load_channel_ids():
    if os.path.exists(CHANNEL_IDS_FILE):
        with open(CHANNEL_IDS_FILE, 'r') as file:
            return json.load(file)
    return {}

def save_channel_ids(channel_ids):
    with open(CHANNEL_IDS_FILE, 'w') as file:
        json.dump(channel_ids, file)

# load channel IDs when the bot starts
channel_ids = load_channel_ids()

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

    await bot.tree.sync()
    print("Slash commands have been synced.")

    # start the daily task if it's not already running
    if not daily_task.is_running():
        daily_task.start()

    # load the channel IDs from the JSON file and ensure they're valid
    for guild_id, channel_id in channel_ids.items():
        guild = bot.get_guild(guild_id)
        if guild:
            channel = guild.get_channel(channel_id)
            if not channel:
                print(f"Stored channel ID {channel_id} is invalid or the channel was deleted in guild {guild.name}.")

@bot.event
async def on_guild_join(guild):
    channel = discord.utils.get(guild.text_channels, name="general")
    
    if channel:
        print(f"Using channel: {channel.name}")
        if channel.permissions_for(guild.me).send_messages:
            await channel.send(
                f"\n**I have arrived to give you random facts, presented by me -- frog 🐸.** "
                f"**To receive your daily dose of facts, please set a channel for me using the `/setchannel` command.**"
            )
        else:
            print(f"Bot does not have permission to send messages in {channel.name}.")
    else:
        print("No suitable text channel found.")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    if 'frog' in message.content.lower():
        await message.add_reaction('🐸')

    await bot.process_commands(message)

@bot.tree.command(name="setchannel", description="Set the channel for daily messages.")
@app_commands.describe(channel="The channel to send daily messages to.")
async def set_channel(interaction: discord.Interaction, channel: discord.TextChannel):
    channel_ids[interaction.guild.id] = channel.id  # Store the channel ID
    save_channel_ids(channel_ids)  # Save the updated channel IDs

    await interaction.response.send_message(f"Daily messages will be sent to {channel.mention}.")
    
    fact = get_random_fact()
    froglish_fact = convert_to_frog(fact)
    frog_pic_url = await fetch_random_frog_picture()

    embed = discord.Embed(
        title="Daily Fact Told By Frog",
        description=f"**Fact:** {fact}\n\n**Fact in Froglish:** {froglish_fact}\n\n**The frog who told you this fact:**",
        color=discord.Color.green()
    )
    embed.set_image(url=frog_pic_url)
    await channel.send(embed=embed)

    now = datetime.now()
    # TODO: Fix the time to be 5 AM UTC instead of the current time
    next_update_time = (now + timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')
    await channel.send(f"**The next update will be on {next_update_time}.**")

@bot.tree.command(name="speak", description="Make the bot speak.")
async def speak(interaction: discord.Interaction):
    frog_quotes = ['I\'m a frog', 'Ribbit']
    response = random.choice(frog_quotes)
    await interaction.response.send_message(response)

@bot.tree.command(name="fact", description="Get a random fact.")
async def fact(interaction: discord.Interaction):
    try:
        fact = get_random_fact()
        froglish_fact = convert_to_frog(fact)
        embed = discord.Embed(
            title="Random Fact",
            description=f"**Fact:** {fact}\n\n**Fact in Froglish:** {froglish_fact}",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed)
    except discord.errors.NotFound:
        await interaction.response.send_message("Failed to fetch fact. Please try again.")

@bot.tree.command(name="frogpic", description="Get a random frog picture.")
async def frogpic(interaction: discord.Interaction):
    try:
        frog_pic_url = await fetch_random_frog_picture()
        embed = discord.Embed(
            title="Random Frog Picture",
            color=discord.Color.green()
        )
        embed.set_image(url=frog_pic_url)
        await interaction.response.send_message(embed=embed)
    except discord.errors.NotFound:
        await interaction.response.send_message("Failed to fetch frog picture. Please try again.")

@bot.tree.command(name="help", description="Get a list of available commands.")
async def help_command(interaction: discord.Interaction):
    help_message = (
        "**Frog Bot Commands:**\n"
        "\n**/setchannel**: Users can set a specific channel to receive daily facts told by a froggo. "
        "The user will see a fact in English and Froglish, with a picture of the froggo who told you that fact.\n"
        "\n**/speak**: The bot outputs a random quote told by a froggo.\n"
        "\n**/fact**: Fetches a random fact along with its translation in Froglish.\n"
        "\n**/frogpic**: Returns a random frog picture.\n"
        "\n**/sync**: Syncs slash commands for the current guild, accessible only by the bot owner.\n"
        "\n**Note**: This bot also reacts with a 🐸 emoji to any message containing the word 'frog'."
    )
    embed = discord.Embed(
        title="Help",
        description=help_message,
        color=discord.Color.green()
    )
    await interaction.response.send_message(embed=embed)


@bot.command(name="sync")
@commands.is_owner()
async def sync(ctx):
    guild = ctx.guild
    await bot.tree.sync(guild=guild)
    await ctx.send(f"Slash commands have been synced with {guild.name}.")

# task that runs every day at 5 AM UTC
@tasks.loop(hours=24)
async def daily_task():
    await bot.wait_until_ready()

    for guild in bot.guilds:
        channel_id = channel_ids.get(guild.id)
        if channel_id is None:
            print(f"No channel set for daily messages in {guild.name}.")
            continue

        channel = bot.get_channel(channel_id)
        if channel is None or not isinstance(channel, discord.TextChannel):
            print(f"Channel not found or is not a text channel in {guild.name}.")
            continue

        try:
            fact = get_random_fact()
            froglish_fact = convert_to_frog(fact)
            frog_pic_url = await fetch_random_frog_picture()

            embed = discord.Embed(
                title="Daily Fact Told By Frog",
                description=f"**Fact:** {fact}\n\n**Fact in Froglish:** {froglish_fact}\n\n**The frog who told you this fact:**",
                color=discord.Color.green()
            )
            embed.set_image(url=frog_pic_url)
            await channel.send(embed=embed)

            now = datetime.utcnow()
            next_update_time = (now + timedelta(days=1)).replace(hour=5, minute=0, second=0, microsecond=0).strftime('%Y-%m-%d %H:%M:%S')
            await channel.send(f"**The next update will be on {next_update_time} UTC.**")
        except discord.errors.HTTPException as e:
            print(f"Rate limit error or other HTTP error: {e}")

@daily_task.before_loop
async def before_daily_task():
    now = datetime.utcnow()
    target_time = now.replace(hour=5, minute=0, second=0, microsecond=0)
    if now > target_time:
        target_time += timedelta(days=1)
    await discord.utils.sleep_until(target_time)

def get_random_fact():
    try:
        response = requests.get('https://uselessfacts.jsph.pl/random.json?language=en')
        if response.status_code == 200:
            data = response.json()
            return data['text']
        else:
            return 'Could not retrieve a fact at this moment.'
    except Exception as e:
        return f'An error occurred: {e}'

def convert_to_frog(fact):
    sounds = ['croak', 'ribbit', 'peep', 'grunt', 'beep']
    froglish = []
    words = fact.split()

    for word in words:
        froglish.append(random.choice(sounds))

    return ' '.join(froglish)

async def fetch_random_frog_picture():
    url = "http://allaboutfrogs.org/funstuff/randomfrog.html"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                html = await resp.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                script_tag = soup.find('script', string=lambda t: "images = new Array(" in t)
                if script_tag:
                    # TODO: use .text instead of .string -- depreacted in bs4 4.9.0
                    images = script_tag.string.split('var images = new Array(')[1].split(');')[0].replace('"', '').split(',')
                    random_image = random.choice(images)
                    return random_image.strip()
                else:
                    return "Could not find a frog image."
            else:
                return "Could not retrieve the frog picture at this time."

@bot.event
async def on_interaction(interaction: discord.Interaction):
    if interaction.type == discord.InteractionType.component:
        await interaction.response.send_message("Interaction received!")

bot.run(TOKEN)
