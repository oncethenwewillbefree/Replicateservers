import discord
from discord.ext import commands
import sys
import asyncio

client = commands.Bot(command_prefix="/", self_bot=True)

def kiz():
    print("This script was made by @kiz.")
    print("It can't be edited or shared without permission.")
    print("\nType 'I agree' to continue.")

def terms():
    if input("> ").lower() != "i agree":
        sys.exit()

def get_serverid():
    original_serv_id = input("Enter the server ID to copy from (the original template server): ")
    target_serv_id = input("Enter the server ID to send to (the server u want to send to): ")
    return int(original_serv_id), int(target_serv_id)

def get_token():
    return input("Enter your token: ")

@client.event
async def on_ready():
    original_serv_id, target_serv_id = get_serverid()
    original_serv = client.get_guild(original_serv_id)
    target_guild = client.get_guild(target_serv_id)

    if not original_serv or not target_guild:
        sys.exit()

    try:
        category_mapping = {}
        
        for category in original_serv.categories:
            new_category = await target_guild.create_category(name=category.name)
            await replicate(category, new_category, target_guild)
            category_mapping[category.id] = new_category

        for category in original_serv.categories:
            sorted_channels = sorted(category.channels, key=lambda x: x.position)
            for channel in sorted_channels:
                if isinstance(channel, discord.TextChannel):
                    new_channel = await target_guild.create_text_channel(
                        name=channel.name, 
                        category=category_mapping[category.id], 
                        position=channel.position
                    )
                elif isinstance(channel, discord.VoiceChannel):
                    new_channel = await target_guild.create_voice_channel(
                        name=channel.name, 
                        category=category_mapping[category.id], 
                        position=channel.position
                    )

                if new_channel:
                    await replicate(channel, new_channel, target_guild)

    except discord.Forbidden:
        pass
    except discord.HTTPException as http_error:
        if http_error.status == 429:
            await asyncio.sleep(http_error.retry_after)  
            await on_ready()

async def replicate(source_channel, target_channel, target_guild):
    overwrites = source_channel.overwrites
    new_overwrites = {}

    for role_or_member, overwrite in overwrites.items():
        if isinstance(role_or_member, discord.Role):
            target_role = discord.utils.get(target_guild.roles, name=role_or_member.name)
            if target_role:
                new_overwrites[target_role] = overwrite

    await target_channel.edit(overwrites=new_overwrites)
kiz()
terms()
client.run(get_token())
