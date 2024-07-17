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

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

    for guild in bot.guilds:
        print(f'Syncing commands for guild: {guild.name} (id: {guild.id})')
        await bot.tree.sync(guild=guild)
    print("Slash commands have been synced with all guilds.")
    
    daily_task.start()  # Start the daily task

@bot.event
async def on_member_join(member):
    await member.create_dm()
    await member.dm_channel.send(f'Hi {member.name}, welcome to my Discord server!')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    if 'frog' in message.content.lower():
        await message.add_reaction('🐸')

    await bot.process_commands(message)

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

@bot.command(name="sync")
@commands.is_owner()
async def sync(ctx):
    guild = ctx.guild
    await bot.tree.sync(guild=guild)
    await ctx.send(f"Slash commands have been synced with {guild.name}.")

@tasks.loop(minutes=1)
async def daily_task():
    await bot.wait_until_ready()
    
    # Get the channel by name
    channel = discord.utils.get(bot.guilds[0].channels, name="general")  # Change "general" to your desired channel name
    if channel is None or not isinstance(channel, discord.TextChannel):
        return  # Exit if the channel doesn't exist or is not a text channel

    fact = get_random_fact()
    froglish_fact = convert_to_frog(fact)
    frog_pic_url = await fetch_random_frog_picture()

    await channel.send(f"**Fact:** {fact}\n**Froglish:** {froglish_fact}")
    await channel.send(frog_pic_url)

@daily_task.before_loop
async def before_daily_task():
    await discord.utils.sleep_until(datetime.now() + timedelta(seconds=60))  # Wait before starting the loop

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
