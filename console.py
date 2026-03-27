import requests
import time

# Skill             |   Skill ID    |   Tool Type
# Masonry           |   4           |   3
# Farming           |   11          |   9
# Carpentry         |   3           |   2
# Smithing          |   6           |   5
# Foraging          |   14          |   12
# Tailoring         |   10          |   8
# Leatherworking    |   8           |   6
# Hunting           |   9           |   7
# Forestry          |   2           |   1
# Mining            |   5           |   4
# Sailing           |   21          |   -
# Fishing           |   12          |   10
# Scholar           |   7           |   13
# Cooking           |   13          |   11 (Pot?)
# Construction      |   15          |   14 (???)
skill = ["0 TELL ME", "ANY", "Forestry", "Carpentry", "Masonry", "Mining", "Smithing", "Scholar", "Leatherworking", "Hunting", "Tailoring", "Farming", "Fishing", "Cooking", "Foraging", "Construction", "16 TELL ME", "17 TELL ME", "18 TELL ME", "19 TELL ME", "20 TELL ME", "Sailing"]
tool = ["0 TELL ME", "Axe", "Saw", "Chisel", "Pickaxe", "Hammer", "Knife", "Bow", "Scissors", "Hoe", "Rod","Pot", "Machete", "Quill", "Shovel?"]

seen_ids = set()

while True:
    try: 
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            for craft in data["craftResults"]:
                if craft["entityId"] not in seen_ids:
                    try:
                        print("Building:",craft["buildingName"])
                        print("Skill:", skill[int(craft["levelRequirements"][0]["skill_id"])])
                        print("required Level:", craft["levelRequirements"][0]["level"])
                        if craft["toolRequirements"]:
                            print("Tool T",craft["toolRequirements"][0]["level"])
                            print("Tooltype:", tool[int(craft["toolRequirements"][0]["tool_type"])])
                        print("Progress:", craft["progress"], "/",craft["totalActionsRequired"])
                        print("Completed:", craft["completed"])
                        print("Owner:", craft["ownerUsername"])
                        print("Public:", craft["isPublic"])
                        print()
                        seen_ids.add(craft["entityId"])
                    except Exception as e:
                        print("Error in parsing craft:", e,"; craft: ",craft)
        else:
            print("Error:", response.status_code)
    except Exception as e:
        print("Fatal Error:", e)
    time.sleep(10)