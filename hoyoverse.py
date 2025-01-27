import os
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
    await bot.sync_all_application_commands()  # Forcing command sync on reboot.
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
    ),
    pull_currency: bool = SlashOption(
        name='pull_currency',
        description='Only show codes including jade/polychromes/primgems/etc.?',
        required=False,
        default=False
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
        'Credit': '<:credit:1333220127826772013>',
        "Traveler's Guide": '<:travelers_guide:1333455919119601664>',
        'Adventure Log': '<:adventure_log:1333456319746932850>',
        # 'Bottled Soda': '<:bottled_soda:1333461270653046835>',
        # 'Potato Fries Sundae': '<:potato_fries_sundae:1333462632438566955>',
        # 'Clockie Pizza (Whole)': '<:clockie_pizza:1333463036589244477>',
        # 'Golden Slumbernana': '<:golden_slumbernana:1333463740753903699>',
        'Lost Gold Fragment': '<:lost_gold_fragment:1333464258272428174>',
        'Refined Aether': '<:refined_aether:1333464643691090000>',
        # 'Automatic Wooden Dummy': '<:automatic_wooden_dummy:1333465283171713126>',
        # 'Alfafa Salad': '<:alfalfa_salad:1333465671727841341>'
    }

    # Fetch the codes data
    codes_data = await getCodes(game)
    if codes_data and 'active' in codes_data:
        active_codes = codes_data['active']

        # Filter codes if pull_currency is True
        if pull_currency:
            currency_items = ['Polychrome', 'Stellar Jade', 'Primogem', 'S-Chip', 'Crystals']
            active_codes = [
                entry for entry in active_codes
                if any(item in reward for reward in entry['rewards'] for item in currency_items)
            ]

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

        # Break the response into chunks of 2000 characters
        summarized = '\n'.join(processed_rewards)
        chunks = []
        current_chunk = 'Currently Active Codes:\n'
        for line in summarized.split('\n'):
            if len(current_chunk) + len(line) + 1 > 2000:
                chunks.append(current_chunk)
                current_chunk = line + '\n'
            else:
                current_chunk += line + '\n'
        if current_chunk:
            chunks.append(current_chunk)

        # Send each chunk as a separate message
        if chunks:
            for i, chunk in enumerate(chunks):
                if i == 0:
                    await interaction.send(chunk)
                else:
                    await interaction.followup.send(chunk)  # Use followup for additional messages
        else:
            await interaction.send('No active codes found matching the criteria.')
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