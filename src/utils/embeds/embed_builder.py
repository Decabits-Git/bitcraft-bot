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
    relative_timestamp = datetime.datetime.now(datetime.UTC)
    title = ":loudspeaker: NEW LARGE CRAFT :loudspeaker:" if is_large_craft else ":tools: New Craft :tools:"
    embed = discord.Embed(color=0xFFFFFF, title=title, timestamp=relative_timestamp)
    embed.set_author(name="LuniBot - Myralune Craft Alert")

    description = ""
    for key, value in embed_description.items():
        description += f'**{key}:** {value}\n'
            
    embed.description = description
    embed.set_footer(text=footer)
    return embed

'''
Function - new_decay_embed
Inputs   - Various strings pertaining to Bitcraft claim info
Outputs  - [Embed] embed : The embed object to send in a Discord message
Purpose  - Create and configure the Discord Embed object for claim decay alerts
'''
def new_decay_embed(
    claim_id: str,
    tier: str,
    claim_name: str,
    claim_owner: str,
    region: str,
    coordinates: str,
    upkeep: str,
    time_remaining: str,
    num_recruitment_slots: str,
    time_since_login: str
) -> discord.Embed:
    
    relative_timestamp = datetime.datetime.now(datetime.UTC)
    title = f'Decaying Claim - {claim_name}'
    claim_bitjita_url = f'https://bitjita.com/claims/{claim_id}'
    embed = discord.Embed(
        color=0xFF6B00,
        title=title,
        url=claim_bitjita_url,
        timestamp=relative_timestamp,
    )
    embed.set_author(name="LuniBot")
    embed.description = f'**Tier: **{tier}\n'
    embed.description += f'**Owner Last Login: **Approx. {time_since_login} days\n'
    embed.description += f'**Open Recruitment Slots: **{num_recruitment_slots}'

    embed.add_field(name="Claim Name", value=claim_name, inline=True)
    embed.add_field(name="Claim Owner", value=claim_owner, inline=True)
    embed.add_field(name="", value="", inline=True)
    embed.add_field(name="Region", value=region, inline=True)
    embed.add_field(name="Coordinates", value=coordinates, inline=True)
    embed.add_field(name="", value="", inline=True)
    embed.add_field(name="Upkeep", value=f'{upkeep}/hr', inline=True)
    embed.add_field(name="Time Remaining", value=f'{time_remaining} hours', inline=True)
    embed.add_field(name="", value="", inline=True)

    embed.set_footer(text=claim_id)
    return embed
