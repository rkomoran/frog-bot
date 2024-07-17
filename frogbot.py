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

# store the channel ID in a dictionary for efficiency 
channel_ids = {}

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

    # sync commands across guilds
    await bot.tree.sync()  
    print("Slash commands have been synced.")

    # have to check if this in not currently running to start or errors
    if not daily_task.is_running():
        daily_task.start()  

    # # test task
    # if not minute_task.is_running():
    #     minute_task.start() 

@bot.event
async def on_guild_join(guild):
    # try to find the general channel as default
    channel = discord.utils.get(guild.text_channels, name="general")
    
    # if general doesn't exist, look for any text channel that has permissions for the bot
    if not channel:
        channel = discord.utils.get(guild.text_channels, permissions=discord.Permissions(send_messages=True))
    
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
    await interaction.response.send_message(f"Daily messages will be sent to {channel.mention}.")
    
    # post a picture and fact right when they set this command. so they know it works
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

    # let them know fact will be ready tomorrow
    now = datetime.now()
    next_update_time = (now + timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')
    await channel.send(f"**The next update will be on {next_update_time}.**")

@bot.tree.command(name="speak", description="Make the bot speak.")
async def speak(interaction: discord.Interaction):
    frog_quotes = ['I\'m a forg', 'Ribbit']
    response = random.choice(frog_quotes)
    await interaction.response.send_message(response)

@bot.tree.command(name="fact", description="Get a random fact.")
async def fact(interaction: discord.Interaction):
    fact = get_random_fact()
    froglish_fact = convert_to_frog(fact)
    embed = discord.Embed(
        title="Random Fact",
        description=f"**Fact:** {fact}\n\n**Fact in Froglish:** {froglish_fact}",
        color=discord.Color.green()
    )
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="frogpic", description="Get a random frog picture.")
async def frogpic(interaction: discord.Interaction):
    frog_pic_url = await fetch_random_frog_picture()
    embed = discord.Embed(
        title="Random Frog Picture",
        color=discord.Color.green()
    )
    embed.set_image(url=frog_pic_url)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="help", description="Get a list of available commands.")
async def help_command(interaction: discord.Interaction):
    help_message = (
        "**Frog Bot Commands:**\n"
        "\n**/setchannel**: Set the channel for daily frog messages. "
        "Usage: `/setchannel <channel>`\n"
        "\n**/speak**: Make the bot say a frog quote. "
        "Usage: `/speak`\n"
        "\n**/fact**: Get a random fact from a frog with a Froglish translation. "
        "Usage: `/fact`\n"
        "\n**/frogpic**: Get a random frog picture. "
        "Usage: `/frogpic`\n"
        "\n**/sync**: Sync slash commands for the current guild (owner only). "
        "Usage: `/sync`\n"
        "\n**Help Command**: Get this list of commands. "
        "Usage: `/help`\n"
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

        embed = discord.Embed(
            title="Daily Fact Told By Frog",
            description=f"**Fact:** {fact}\n\n**Fact in Froglish:** {froglish_fact}\n\n**The frog who told you this fact:**",
            color=discord.Color.green()
        )
        embed.set_image(url=frog_pic_url)
        await channel.send(embed=embed)

        now = datetime.now()
        next_update_time = (now + timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')
        await channel.send(f"**The next update will be on {next_update_time}.**")

@daily_task.before_loop
async def before_daily_task():
    now = datetime.now()
    target_time = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    await discord.utils.sleep_until(target_time)


# @tasks.loop(hours=3)
# async def daily_task():
#     await bot.wait_until_ready()

#     for guild in bot.guilds:
#         channel_id = channel_ids.get(guild.id)
#         if channel_id is None:
#             print(f"No channel set for daily messages in {guild.name}.")
#             continue

#         channel = bot.get_channel(channel_id)
#         if channel is None or not isinstance(channel, discord.TextChannel):
#             print(f"Channel not found or is not a text channel in {guild.name}.")
#             continue

#         fact = get_random_fact()
#         froglish_fact = convert_to_frog(fact)
#         frog_pic_url = await fetch_random_frog_picture()

#         embed = discord.Embed(
#             title="Daily Fact Told By Frog",
#             description=f"**Fact:** {fact}\n\n**Fact in Froglish:** {froglish_fact}\n\n**The frog who told you this fact:**",
#             color=discord.Color.green()
#         )
#         embed.description=f"**The frog who told you this fact:**\n"
#         embed.set_image(url=frog_pic_url)
#         await channel.send(embed=embed)
        
#         now = datetime.now()
#         next_update_time = (now + timedelta(hours=3)).strftime('%Y-%m-%d %H:%M:%S')
#         await channel.send(f"**The next update will be on {next_update_time}.**")

# @daily_task.before_loop
# async def before_daily_task():
#     now = datetime.now()
#     target_time = (now + timedelta(hours=3)).replace(minute=0, second=0, microsecond=0)
#     await discord.utils.sleep_until(target_time)

# test function
# @tasks.loop(minutes=1)
# async def minute_task():
#     await bot.wait_until_ready()

#     for guild in bot.guilds:
#         channel_id = channel_ids.get(guild.id)
#         if channel_id is None:
#             print(f"No channel set for minute messages in {guild.name}.")
#             continue

#         channel = bot.get_channel(channel_id)
#         if channel is None or not isinstance(channel, discord.TextChannel):
#             print(f"Channel not found or is not a text channel in {guild.name}.")
#             continue

#         fact = get_random_fact()
#         froglish_fact = convert_to_frog(fact)
#         frog_pic_url = await fetch_random_frog_picture()

#         embed = discord.Embed(
#             title="Minute Fact Told By Frog",
#             description=f"**Fact:** {fact}\n\n**Fact in Froglish:** {froglish_fact}\n\n**The frog who told you this fact:**",
#             color=discord.Color.green()
#         )
#         embed.set_image(url=frog_pic_url)
#         await channel.send(embed=embed)
        
#         now = datetime.now()
#         next_update_time = (now + timedelta(hours=3)).strftime('%Y-%m-%d %H:%M:%S')
#         await channel.send(f"**The next update will be on {next_update_time}.**")

#         await channel.send("This is a test message sent every minute.")

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
                
                # getting img from html from soup parser (this was hard to figure out)
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
