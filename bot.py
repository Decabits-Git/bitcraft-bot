import discord
import requests
import asyncio
import src.utils.embeds.embed_builder as embed

TOKEN = 
CHANNEL_ID = 

SLEEPTIME = 30
DEFAULT_EFFORT_REQ = 50000
MINIMUM_EFFORT_REQ = 10000

intents = discord.Intents.default()
intents.message_content = True
bot = discord.Client(intents=intents)

### BitCraft Mapping Lists
skill = ["0 TELL ME", "ANY", "Forestry", "Carpentry", "Masonry", "Mining", "Smithing", "Scholar", "Leatherworking", "Hunting", "Tailoring", "Farming", "Fishing", "Cooking", "Foraging", "Construction", "16 TELL ME", "17 TELL ME", "18 TELL ME", "19 TELL ME", "20 TELL ME", "Sailing"]
tool = ["0 TELL ME", "Axe", "Saw", "Chisel", "Pickaxe", "Hammer", "Knife", "Bow", "Scissors", "Hoe", "Rod","Pot", "Machete", "Quill", "Shovel?"]
tool_icons = ["None", ":axe:", ":carpentry_saw:", "Chisel", ":pick:", ":hammer:", ":knife:", ":archery:", ":scissors:", "Hoe", ":fishing_pole_and_fish:", ":cooking:", "Machete", ":feather:", "Shovel?"]

ping_role = ["", "", "<@&1464743725208174704>", "<@&1464743105755353357>", "<@&1464743842870857728>", "<@&1464744033350848644>", "<@&1464744101013356564>", "<@&1464744082684514507>", "<@&1464743781634015517>", "<@&1464743760528150733>", "<@&1464744135167705263>", "<@&1464743374434078820>", "<@&1464743657822228500>", "", "<@&1464743698565697761>", "", "", "", "", "", "", ""]
effort_thresholds_by_profession = {
    "Carpentry"      : DEFAULT_EFFORT_REQ,
    "Cooking"        : 20000,
    "Farming"        : DEFAULT_EFFORT_REQ,
    "Fishing"        : 35000,
    "Foraging"       : 30000,
    "Forestry"       : 30000,
    "Hunting"        : 15000,
    "Leatherworking" : 45000,
    "Masonry"        : 30000,
    "Mining"         : DEFAULT_EFFORT_REQ,
    "Scholar"        : 20000,
    "Smithing"       : DEFAULT_EFFORT_REQ,
    "Tailoring"      : DEFAULT_EFFORT_REQ
}

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
Function - test_for_duplicate_message
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
async def send_thread_message(content: str, embed: discord.Embed, skill: str, entity_id: str, channel: discord.channel.ForumChannel):
    if (await test_for_duplicate_message(entity_id=entity_id, channel=channel)):
        return
    for thread in channel.threads:
        if thread.name == skill:
            await thread.send(content=content, embed=embed, allowed_mentions=discord.AllowedMentions.all())
            seen_ids.add(entity_id)

'''
Function - prune_old_crafts
Inputs   - [ForumChannel] channel : Channel object for the forum to delete messages from
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
                await prune_old_crafts(channel=channel)
                for craft in data["craftResults"]:
                    if craft["entityId"] not in seen_ids:
                        skill_name = skill[int(craft["levelRequirements"][0]["skill_id"])]
                        if int(craft["totalActionsRequired"]) >= MINIMUM_EFFORT_REQ:
                            try:
                                building_name = craft["buildingName"]
                                level_value = craft["levelRequirements"][0]["level"]
                                effort_value = craft["totalActionsRequired"]
                                owner_name = craft["ownerUsername"]
                                embed_description = {
                                    "Building" : building_name,
                                    "Skill"    : skill_name,
                                    "Level"    : level_value,
                                    "Effort"   : effort_value
                                }

                                if craft["toolRequirements"]:
                                    tool_icon = tool_icons[int(craft["toolRequirements"][0]["tool_type"])]
                                    embed_description["Tool"] = tool_icon

                                embed_description["Owner"] = owner_name
                                entity_id = craft["entityId"]

                                message_content = ""
                                is_large_craft=False
                                if int(craft["totalActionsRequired"]) >= effort_thresholds_by_profession[skill_name]:
                                    message_content = ping_role[int(craft["levelRequirements"][0]["skill_id"])]
                                    is_large_craft = True

                                craft_embed = embed.new_craft_embed(
                                    is_large_craft=is_large_craft,
                                    embed_description=embed_description,
                                    footer=entity_id
                                )
                                await send_thread_message(
                                    content=message_content,
                                    embed=craft_embed,
                                    skill=skill_name,
                                    entity_id=entity_id,
                                    channel=channel
                                )

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
