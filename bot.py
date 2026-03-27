import discord
import requests
import asyncio
import src.utils.embeds.embed_builder as embed

TOKEN = ""
CHANNEL_ID =  

intents = discord.Intents.default()
bot = discord.Client(intents=intents)

skill = ["0 TELL ME", "ANY", "Forestry", "Carpentry", "Masonry", "Mining", "Smithing", "Scholar", "Leatherworking", "Hunting", "Tailoring", "Farming", "Fishing", "Cooking", "Foraging", "Construction", "16 TELL ME", "17 TELL ME", "18 TELL ME", "19 TELL ME", "20 TELL ME", "Sailing"]
tool = ["0 TELL ME", "Axe", "Saw", "Chisel", "Pickaxe", "Hammer", "Knife", "Bow", "Scissors", "Hoe", "Rod","Pot", "Machete", "Quill", "Shovel?"]
tool_icons = ["None", ":axe:", ":carpentry_saw:", "Chisel", ":pick:", ":hammer:", ":knife:", ":archery:", ":scissors:", "Hoe", ":fishing_pole_and_fish:", ":cooking:", "Machete", ":feather:", "Shovel?"]

# ClaimID Myralune = 648518346354446795
url = "https://bitjita.com/api/crafts?claimEntityId=648518346354446795"
seen_ids = set()

async def poll_data():
    await bot.wait_until_ready()
    channel = bot.get_channel(CHANNEL_ID)

    while not bot.is_closed():
        try:
            response = requests.get(url)

            if response.status_code == 200:
                data = response.json()

                for craft in data["craftResults"]:
                    if craft["entityId"] not in seen_ids:
                        if int(craft["totalActionsRequired"]) > 20000:
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
                                
                                await channel.send(embed=craft_embed)

                                seen_ids.add(craft["entityId"])

                            except Exception as e:
                                print("Error parsing:", e)

            else:
                print("Error:", response.status_code)

        except Exception as e:
            print("Fatal Error:", e)

        await asyncio.sleep(10)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    bot.loop.create_task(poll_data())


bot.run(TOKEN)
