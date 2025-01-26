import nextcord
from nextcord.ext import commands
from dotenv import load_dotenv
import os

load_dotenv()

guild_id = os.getenv('TESTING_GUID_ID')
token = os.getenv('BOT_TOKEN')

bot = commands.Bot()

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.slash_command(description="Sample slash command", guild_ids=[guild_id])
async def hello(interaction: nextcord.Interaction):
    await interaction.send("Hello!")

bot.run(token)
