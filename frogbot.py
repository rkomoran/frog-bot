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

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# Store the channel ID in a dictionary (or a database for more complexity)
channel_ids = {}

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

    await bot.tree.sync()  # Sync commands globally
    print("Slash commands have been synced.")

    if not daily_task.is_running():
        daily_task.start()  # Start the daily task

@bot.event
async def on_guild_join(guild):
    # Try to find the "general" channel
    channel = discord.utils.get(guild.text_channels, name="general")
    
    # If "general" doesn't exist, look for any text channel
    if not channel:
        channel = discord.utils.get(guild.text_channels, permissions=discord.Permissions(send_messages=True))
    
    if channel:
        print(f"Using channel: {channel.name}")
        if channel.permissions_for(guild.me).send_messages:
            await channel.send(
                f"\n**Hello everyone! I'm your friendly frog bot 🐸.** "
                f"**To receive your daily dose of facts, please set a channel for daily frog facts using the `/setchannel` command.**"
            )
        else:
            print(f"Bot does not have permission to send messages in {channel.name}.")
    else:
        print("No suitable text channel found.")

# @bot.event
# async def on_member_join(member):
#     await member.create_dm()
#     await member.dm_channel.send(f'Hi {member.name}, welcome to my Discord server!')

# @bot.event
# async def on_message(message):
#     if message.author == bot.user:
#         return
    
#     if 'frog' in message.content.lower():
#         await message.add_reaction('🐸')

#     await bot.process_commands(message)

@bot.tree.command(name="setchannel", description="Set the channel for daily messages.")
@app_commands.describe(channel="The channel to send daily messages to.")
async def set_channel(interaction: discord.Interaction, channel: discord.TextChannel):
    channel_ids[interaction.guild.id] = channel.id  # Store the channel ID
    await interaction.response.send_message(f"Daily messages will be sent to {channel.mention}.")

@bot.tree.command(name="speak", description="Make the bot say a frog quote.")
async def speak(interaction: discord.Interaction):
    frog_quotes = ['I\'m a forg', 'Ribbit']
    response = random.choice(frog_quotes)
    await interaction.response.send_message(response)

@bot.tree.command(name="fact", description="Get a random fact.")
async def fact(interaction: discord.Interaction):
    fact = get_random_fact()
    froglish_fact = convert_to_frog(fact)
    await interaction.response.send_message(f"**Fact:** {fact}\n**Froglish:** {froglish_fact}")

@bot.tree.command(name="frogpic", description="Get a random frog picture.")
async def frogpic(interaction: discord.Interaction):
    frog_pic_url = await fetch_random_frog_picture()
    await interaction.response.send_message(frog_pic_url)

@bot.tree.command(name="help", description="Get a list of available commands.")
async def help_command(interaction: discord.Interaction):
    help_message = (
        "**Frog Bot Commands:**\n"
        "\n**/setchannel**: Set the channel for daily frog messages. "
        "Usage: `/setchannel <channel>`\n"
        "\n**/speak**: Make the bot say a frog quote. "
        "Usage: `/speak`\n"
        "\n**/fact**: Get a random fact about frogs with a Froglish translation. "
        "Usage: `/fact`\n"
        "\n**/frogpic**: Get a random frog picture. "
        "Usage: `/frogpic`\n"
        "\n**/sync**: Sync slash commands for the current guild (owner only). "
        "Usage: `/sync`\n"
        "\n**Help Command**: Get this list of commands. "
        "Usage: `/help`\n"
    )
    await interaction.response.send_message(help_message)

@bot.command(name="sync")
@commands.is_owner()
async def sync(ctx):
    guild = ctx.guild
    await bot.tree.sync(guild=guild)
    await ctx.send(f"Slash commands have been synced with {guild.name}.")

# @tasks.loop(hours=24)
# async def daily_task():
#     await bot.wait_until_ready()
    
#     # Iterate through all guilds and send messages to the configured channel
#     for guild in bot.guilds:
#         channel_id = channel_ids.get(guild.id)
#         if channel_id is None:
#             print(f"No channel set for daily messages in {guild.name}.")
#             continue  # Skip this guild if no channel is set

#         channel = bot.get_channel(channel_id)
#         if channel is None or not isinstance(channel, discord.TextChannel):
#             print(f"Channel not found or is not a text channel in {guild.name}.")
#             continue  # Skip if the channel doesn't exist or isn't a text channel

#         fact = get_random_fact()
#         froglish_fact = convert_to_frog(fact)
#         frog_pic_url = await fetch_random_frog_picture()

#         await channel.send(f"**Fact:** {fact}\n**Froglish:** {froglish_fact}")
#         await channel.send(frog_pic_url)

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

        fact = get_random_fact()
        froglish_fact = convert_to_frog(fact)
        frog_pic_url = await fetch_random_frog_picture()

        await channel.send(f"**Fact:** {fact}\n**Froglish:** {froglish_fact}")
        await channel.send(frog_pic_url)

@daily_task.before_loop
async def before_daily_task():
    now = datetime.now()
    target_time = now.replace(hour=0, minute=1, second=0, microsecond=0)
    if now > target_time:
        target_time += timedelta(days=1)
    await discord.utils.sleep_until(target_time)

# @daily_task.before_loop
# async def before_daily_task():
#     await discord.utils.sleep_until(datetime.now() + timedelta(seconds=60))  # Wait before starting the loop

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
                
                script_tag = soup.find('script', text=lambda t: "images = new Array(" in t)
                if script_tag:
                    images = script_tag.string.split('var images = new Array(')[1].split(');')[0].replace('"', '').split(',')
                    random_image = random.choice(images)
                    return random_image.strip()
                else:
                    return "Could not find a frog image."
            else:
                return "Could not retrieve the frog picture at this time."

bot.run(TOKEN)
