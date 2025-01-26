import os
import re
import requests
import nextcord
from nextcord.ext import commands
from nextcord import SlashOption
from dotenv import load_dotenv

load_dotenv()

guild_id = os.getenv('TESTING_GUILD_ID')
token = os.getenv('BOT_TOKEN')
api_url = os.getenv('API_URL')

bot = commands.Bot()

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    await bot.sync_all_application_commands() # Forcing command sync on reboot.
    print("Slash commands synced!")

@bot.slash_command(description="Retrieve active codes.", guild_ids=[guild_id])
async def codes(
    interaction: nextcord.Interaction,
    game: str = SlashOption(
        name='game',
        description='Choose your game',
        choices={
            'Genshin Impact': 'genshin',
            'Honkai Star Rail': 'starrail',
            'Honkai Impact 3rd': 'honkai',
            'Tears of Themis': 'themis',
            'Zenless Zone Zero': 'zenless'
        }
    )
):
    # Mapping of items to their corresponding image URLs
    item_images = {
        'Polychrome': '<:polychrome:1333207418993381407>',
        'Denny': '<:denny:1333208441627475978>',
        'Dennies': '<:denny:1333208441627475978>',
        'Official Investigator Log': '<:official_investigator_log:1333208670523359313>',
        'Senior Investigator Log': '<:senior_investigator_log:1333208880414720061>',
        'W-Engine Power Supply': '<:wengine_power_supply:1333209135650439188>',
        'W-Engine Energy Module': '<:wengine_energy_module:1333209406610997349>',
        'Bangboo Algorithm Module': '<:bangboo_algorithm_module:1333209661607776408>',
        'Ether Battery': '<:ether_battery:1333209908253954078>',
        'Ether Plating Agent': '<:ether_plating_agent:1333210164630650972>',
        'Crystallized Plating Agent': '<:crystallized_plating_agent:1333210599466729624>',
        'Primogem': '<:primogem:1333216755346182154>',
        'Mora': '<:mora:1333217292334661764>',
        "Hero's Wit": '<:heros_wit:1333217927230394441>',
        "Adventurer's Experience": '<:adventurers_experience:1333218374242533447>',
        'Mystic Enhancement Ore': '<:mystic_enhancement_ore:1333218863248179260>',
        'Stellar Jade': '<:stellar_jade:1333219716390719641>',
        'Credit': '<:credit:1333220127826772013>'
    }

    # Fetch the codes data
    codes_data = await getCodes(game)
    if codes_data and 'active' in codes_data:
        active_codes = codes_data['active']

        # Process rewards to replace names with image URLs
        processed_rewards = []
        for entry in active_codes:
            formatted_rewards = []
            for reward in entry['rewards']:
                for item, image_url in item_images.items():
                    if item in reward:
                        reward = reward.replace(item, f'{image_url}')
                formatted_rewards.append(reward)
            processed_rewards.append(f"**{entry['code']}** ({', '.join(formatted_rewards)})")

        # Build and send the message
        summarized = '\n'.join(processed_rewards)
        await interaction.send(f'Currently Active Codes:\n{summarized[:2000]}')  # Ensure message length <= 2000
    else:
        await interaction.send('No active codes found or an error occurred.')
    

async def getCodes(game: str):
    response = requests.get(f'{api_url}/{game}/codes')
    if response.status_code == 200:
        print("Response JSON:")
        print(response.json())  # Parsed JSON response
        return response.json()
    else:
        print(f"Failed to fetch. Status Code: {response.status_code}")
        return None

bot.run(token)
