import discord
import requests
import asyncio
import src.utils.embeds.embed_builder as embed

TOKEN = ""
CHANNEL_ID =  
SLEEPTIME = 

intents = discord.Intents.default()
intents.message_content = True
bot = discord.Client(intents=intents)

### BitCraft Mapping Lists
skill = ["0 TELL ME", "ANY", "Forestry", "Carpentry", "Masonry", "Mining", "Smithing", "Scholar", "Leatherworking", "Hunting", "Tailoring", "Farming", "Fishing", "Cooking", "Foraging", "Construction", "16 TELL ME", "17 TELL ME", "18 TELL ME", "19 TELL ME", "20 TELL ME", "Sailing"]
tool = ["0 TELL ME", "Axe", "Saw", "Chisel", "Pickaxe", "Hammer", "Knife", "Bow", "Scissors", "Hoe", "Rod","Pot", "Machete", "Quill", "Shovel?"]
tool_icons = ["None", ":axe:", ":carpentry_saw:", "Chisel", ":pick:", ":hammer:", ":knife:", ":archery:", ":scissors:", "Hoe", ":fishing_pole_and_fish:", ":cooking:", "Machete", ":feather:", "Shovel?"]

# ClaimID Myralune = 648518346354446795
url = "https://bitjita.com/api/crafts?claimEntityId=648518346354446795"
seen_ids = set()  # ids of crafts that have been seen/processed by the bot

##### Functions #####

'''
Function - remove_old_ids
Inputs   - [dict] data : JSON response from the BitJita endpoint
Outputs  - N/A
Purpose  - Clean up any completed crafts from seen_ids; allows messages to be deleted from Discord
'''
def remove_old_ids(data: dict):
    if (seen_ids == set()):
        return

    jita_ids = []
    for craft in data["craftResults"]:
        jita_ids.append(craft["entityId"])

    delete_ids = []
    for id in seen_ids:
        if id not in jita_ids:
            delete_ids.append(id)
    
    for id in delete_ids:
        seen_ids.remove(id)

'''
Function - check_for_duplicate_message
Inputs   - [str] entity_id        : The ID of a craft at a BitCraft station
           [ForumChannel] channel : Channel object for the forum to check for duplicate entityId
Outputs  - [bool]                 : A boolean indicating whether or not the entityId has been messaged previously
Purpose  - Return true/false to indicate whether a craft has been alerted on to prevent duplicates
'''
async def test_for_duplicate_message(entity_id: str, channel: discord.channel.ForumChannel):
    for thread in channel.threads:
        async for message in thread.history(limit=100):
            if (message.embeds != []) and (message.embeds != None):
                for embed in message.embeds:
                    if embed.footer.text == entity_id:
                        return True
    return False

'''
Function - send_thread_message
Inputs   - [Embed] embed          : The embed object to send to the Discord thread
           [str] skill            : The skill name of the craft
           [str] entity_id        : The ID of the craft at the station
           [ForumChannel] channel : The forum channel the message will be sent in
Outputs  - N/A
Purpose  - Send the craft alert to Discord
'''
async def send_thread_message(embed: discord.Embed, skill: str, entity_id: str, channel: discord.channel.ForumChannel):
    if (await test_for_duplicate_message(entity_id=entity_id, channel=channel)):
        return
    for thread in channel.threads:
        if thread.name == skill:
            await thread.send(embed=embed)
            seen_ids.add(entity_id)

'''
Function - prune_old_crafts
Inputs   - [dict]         data    : JSON response from the BitJita endpoint
           [ForumChannel] channel : Channel object for the forum to delete messages from
Outputs  - N/A
Purpose  - Delete messages for completed crafts from the provided Discord channel
'''
async def prune_old_crafts(channel: discord.channel.ForumChannel):
    for thread in channel.threads:
        async for message in thread.history(limit=100):
            if (message.embeds != []) and (message.embeds != None):
                for embed in message.embeds:
                    if embed.footer.text not in seen_ids:
                        await message.delete()
                            
'''
Function - poll_data
Inputs   - N/A
Outputs  - N/A
Purpose  - Main loop; orchestrate crafting alerts and send messages to relevant channels
'''
async def poll_data():
    await bot.wait_until_ready()
    channel = bot.get_channel(CHANNEL_ID)

    while not bot.is_closed():
        try:
            response = requests.get(url)

            if response.status_code == 200:
                data = response.json()
                remove_old_ids(data)
                for craft in data["craftResults"]:
                    if craft["entityId"] not in seen_ids:
                        if int(craft["totalActionsRequired"]) > 100000:
                            try:
                                building_name = craft["buildingName"]
                                skill_name = skill[int(craft["levelRequirements"][0]["skill_id"])]
                                level_value = craft["levelRequirements"][0]["level"]
                                effort_value = craft["totalActionsRequired"]
                                owner_name = craft["ownerUsername"]
                                if craft["toolRequirements"]:
                                    tool_icon = tool_icons[int(craft["toolRequirements"][0]["tool_type"])]
                                    craft_embed = embed.new_craft_embed(
                                        Building=building_name,
                                        Skill=skill_name,
                                        Level=level_value,
                                        Effort=effort_value,
                                        Tool=tool_icon,
                                        Owner=owner_name
                                    )
                                else:
                                    craft_embed = embed.new_craft_embed(
                                        Building=building_name,
                                        Skill=skill_name,
                                        Level=level_value,
                                        Effort=effort_value,
                                        Owner=owner_name
                                    )

                                entity_id = craft["entityId"]
                                craft_embed.set_footer(text=entity_id)

                                await send_thread_message(embed=craft_embed, skill=skill_name, entity_id=entity_id, channel=channel)
                                await prune_old_crafts(channel=channel)

                            except Exception as e:
                                print("Error parsing:", e)

            else:
                print("Error:", response.status_code)

        except Exception as e:
            print("Fatal Error:", e)

        await asyncio.sleep(SLEEPTIME)

'''
Function - on_ready
Inputs   - N/A
Outputs  - N/A
Purpose  - Initialize the bot
'''
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    bot.loop.create_task(poll_data())

bot.run(TOKEN)
