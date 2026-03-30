import discord
import datetime

'''
Function - new_craft_embed
Inputs   - **kwargs      : Dynamic number of key/value pairs to insert into Embed description
Outputs  - [Embed] embed : The Embed object to send in a Discord message
Purpose  - Create and configure the Discord Embed object for crafting alerts
'''
def new_craft_embed(**kwargs):
    relative_timestamp = datetime.datetime.now(datetime.timezone.utc)
    embed = discord.Embed(color=0xFFFFFF, title=":loudspeaker: NEW LARGE CRAFT :loudspeaker:", timestamp=relative_timestamp)
    embed.set_author(name="LuniBot - Myralune Craft Alert")

    description = ""
    for k, val in kwargs.items():
        description += f'**{k}:** {val}\n'
            
    embed.description = description
    return embed
