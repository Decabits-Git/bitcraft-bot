import asyncio
import datetime
import discord
import logging
import src.utils.embeds.embed_builder as embed
import src.utils.http.request as http_request

################################################################################
##### Variables #####
################################################################################

SLEEPTIME = 30
DEFAULT_EFFORT_REQ = 50000
MINIMUM_EFFORT_REQ = 10000

### Discord
TOKEN = 
CHANNEL_ID = {
    "Craft" : ,
    "Decay" : ,
}

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
claim_craft_url = "https://bitjita.com/api/crafts?claimEntityId=648518346354446795"
seen_ids = set()  # ids of crafts that have been seen/processed by the bot

claim_url = "https://bitjita.com/api/claims"

################################################################################
##### Functions #####
################################################################################

'''
Function - remove_old_ids
Inputs   - [dict] data : JSON response from the BitJita endpoint
Outputs  - N/A
Purpose  - Clean up any completed crafts from seen_ids; allows messages to be deleted from Discord
'''
def remove_old_ids(data: dict):
    if (seen_ids == set()):
        return
    
    """
    Workflow:
        1. Identify all craft entityIds for the claim from BitJita
        2. Track any Ids processed previously that are not present in the latest BitJita query
        3. Delete the tracked Ids from the seen_ids set so that old crafts can be pruned from Discord
    """

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

    """
    Workflow:
        1. Iterate through all threads, and then through all messages in each thread to see if there are embeds
        2. If there is an embed, and its footer matches the entity_id provided to the function, that means the current
           entity_id is a duplicate and does not need to be alerted on
    """

    for thread in channel.threads:
        try:
            async for message in thread.history(limit=100):
                if (message.embeds != []) and (message.embeds != None):
                    for embed in message.embeds:
                        if embed.footer.text == entity_id:
                            return True
        except discord.DiscordException as e:
            print("Discord Thread History Error:", e)

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
    
    """
    Workflow:
        1. Identify the correct thread to send the alert to based on BitCraft profession
        2. Take note of the current craft's entity_id so it can eventually be pruned after completion
    """

    for thread in channel.threads:
        if thread.name == skill:
            try:
                await thread.send(content=content, embed=embed, allowed_mentions=discord.AllowedMentions.all())
            except discord.DiscordException as e:
                print("Discord Send Message Error:", e)

            seen_ids.add(entity_id)

'''
Function - prune_old_crafts
Inputs   - [ForumChannel] channel : Channel object for the forum to delete messages from
Outputs  - N/A
Purpose  - Delete messages for completed crafts from the provided Discord channel
'''
async def prune_old_crafts(channel: discord.channel.ForumChannel):

    """
    Workflow:
        1. Iterate through thread message history in the Discord forum to look for embeds
        2. If an embed footer is not present in seen_ids, the Discord message can be deleted
    """

    for thread in channel.threads:
        async for message in thread.history(limit=100):
            if (message.embeds != []) and (message.embeds != None):
                for embed in message.embeds:
                    if embed.footer.text not in seen_ids:
                        await message.delete()
                            
'''
Function - poll_claim_craft_data
Inputs   - N/A
Outputs  - N/A
Purpose  - Orchestrate crafting alerts and send messages to relevant channels
'''
async def poll_claim_craft_data():
    await bot.wait_until_ready()
    channel = bot.get_channel(CHANNEL_ID["Craft"])

    """
    Workflow:
        1. Get claim craft results from BitJita
        2. Iterate through all crafts at the claim and identify those with sufficient effort for alerting
        3. Build the Discord embed with the craft information, and send it to the appropriate Discord thread
    """

    ping_allowed = False
    while not bot.is_closed():
        data = await http_request.get(url=claim_craft_url)

        remove_old_ids(data)
        await prune_old_crafts(channel=channel)

        for craft in data["craftResults"]:
            if craft["entityId"] not in seen_ids:
                skill_name = skill[int(craft["levelRequirements"][0]["skill_id"])]
                if int(craft["totalActionsRequired"]) >= MINIMUM_EFFORT_REQ:
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
                            if (ping_allowed):
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

        ping_allowed = True
        await asyncio.sleep(SLEEPTIME)

'''
Function - poll_claim_decay_data
Inputs   - N/A
Outputs  - N/A
Purpose  - Identify and alert on claims with open recruitment that will decay within 3 days
'''
async def poll_claim_decay_data():
    await bot.wait_until_ready()
    channel = bot.get_channel(CHANNEL_ID["Decay"])

    """
    Workflow:
        1. Get the list of all BitCraft claims from BitJita
        2. Iterate through all of the claims to identify any that are close to decaying and have open recruitment slots
        3. Build a Discord embed with the data and send it to the appropriate Discord channel
    """

    page_number = 1
    http_params = {
        "page"  : page_number,
        "limit" : 100
    }

    data = await http_request.get(url=claim_url, params=http_params)
    while data["claims"] != []:
        for claim in data["claims"]:
            current_claim_url = claim_url + "/" + claim["entityId"]

            claim_data = await http_request.get(url=current_claim_url)
            supplies = int(claim_data["claim"]["supplies"])
            upkeep_cost = claim_data["claim"]["upkeepCost"]

            hours_until_decay = round(supplies / upkeep_cost)
            if (hours_until_decay <= 72):
                claim_recruit_url = current_claim_url + "/recruitment"
                recruitment_data = await http_request.get(url=claim_recruit_url)
                if recruitment_data["recruitment"] == []:
                    continue

                num_recruitment_slots = recruitment_data["recruitment"][0]["remainingStock"]
                if int(num_recruitment_slots) <= 0:
                    continue

                owner_url = f'https://bitjita.com/api/players/{claim_data["claim"]["ownerPlayerEntityId"]}'
                owner_data = await http_request.get(url=owner_url)
                if owner_data["player"]["signedIn"] == "true":
                    continue

                owner_last_login = datetime.datetime.strptime(owner_data["player"]["lastLoginTimestamp"], "%Y-%m-%d %H:%M:%S+00")
                time_since_login = datetime.datetime.now(datetime.UTC) - owner_last_login.astimezone(datetime.UTC)

                claim_id = claim_data["claim"]["entityId"]
                tier = claim_data["claim"]["tier"]
                claim_name = claim_data["claim"]["name"]
                claim_owner = claim_data["claim"]["ownerPlayerUsername"]
                region = claim_data["claim"]["regionId"]
                coordinates = f'N:{round(int(claim_data["claim"]["locationZ"]) / 3)} E:{round(int(claim_data["claim"]["locationX"]) / 3)}'
                upkeep = str(round(float(claim_data["claim"]["upkeepCost"])))
                decay_embed = embed.new_decay_embed(
                    claim_id=claim_id,
                    tier=tier,
                    claim_name=claim_name,
                    claim_owner=claim_owner,
                    region=region,
                    coordinates=coordinates,
                    upkeep=upkeep,
                    time_remaining=str(hours_until_decay),
                    num_recruitment_slots=num_recruitment_slots,
                    time_since_login=str(time_since_login.days),
                )

                await channel.send(embed=decay_embed)

        page_number += 1
        http_params["page"] = page_number
        data = await http_request.get(url=claim_url, params=http_params)
    
    await asyncio.sleep(3600)

################################################################################
##### Bot Events #####
################################################################################

'''
Function - on_ready
Inputs   - N/A
Outputs  - N/A
Purpose  - Initialize the bot
'''
@bot.event
async def on_ready():
    if not hasattr(bot, "polling_started"):
        bot.polling_started = True
        logging.info(f"Logged in as {bot.user}")
        bot.loop.create_task(poll_claim_craft_data())
        bot.loop.create_task(poll_claim_decay_data())

################################################################################
##### Main #####
################################################################################

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    bot.run(TOKEN)

