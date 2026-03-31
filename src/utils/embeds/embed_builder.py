import discord
import datetime

'''
Function - new_craft_embed
Inputs   - [bool] is_large_craft : True if a craft is large, False if not
           [dict] embed_description : Custom key-value pairs containing the description for the Embed
           [str] footer : The text to be inserted into the footer of the embed object, conventionally an entityId
Outputs  - [Embed] embed : The Embed object to send in a Discord message
Purpose  - Create and configure the Discord Embed object for crafting alerts
'''
def new_craft_embed(is_large_craft: bool, embed_description: dict, footer: str):
    relative_timestamp = datetime.datetime.now(datetime.timezone.utc)
    title = ":loudspeaker: NEW LARGE CRAFT :loudspeaker:" if is_large_craft else ":tools: New Craft :tools:"
    embed = discord.Embed(color=0xFFFFFF, title=title, timestamp=relative_timestamp)
    embed.set_author(name="LuniBot - Myralune Craft Alert")

    description = ""
    for key, value in embed_description.items():
        description += f'**{key}:** {value}\n'
            
    embed.description = description
    embed.set_footer(text=footer)
    return embed
