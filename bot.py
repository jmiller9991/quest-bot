import os
import discord
import json
from discord.ext import commands
import sqlite3
import asyncio



# JSON Prefixes
async def get_prefix(client, message):
    with open('prefixes.json', 'r') as f:
        prefixes = json.load(f)

    return prefixes[str(message.guild.id)]

client = commands.Bot(command_prefix=get_prefix)

########################################################################################################################
#   EVENTS                                                                                                             #
########################################################################################################################

# readys the bot
@client.event
async def on_ready():
    db = sqlite3.connect('main.sqlite')
    cursor = db.cursor()

    #Create db of quest total
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS quest_list(
            guild_id TEXT,
            quest_number TEXT,
            quest_title TEXT,
            quest_description TEXT,
            author_name TEXT,
            author_image TEXT,
            reward_type TEXT,
            quest_accepted_date TEXT,
            quest_image TEXT,
            quest_challenge TEXT,
            quest_status TEXT          
        }
    ''')

    print('Quest Table Complete')

    db.commit()
    cursor.close()
    db.close()

# joins guild info
@client.event
async def on_guild_join(guild):
    #set default prefix
    with open('prefixes.json', 'r') as f:
        prefixes = json.load(f)

    prefixes[str(guild.id)] = '!'

    with open('prefixes.json', 'w') as f:
        json.dump(prefixes, f, indent=4)
    #sends message
    for channel in guild.text_channels:
        if channel.permissions_for(guild.me).send_messages:
            await channel.send(f'''
            ```Hello there! Thank you for adding tabletop-quest-bot to your Discord server!
            This bot was written in API version {discord.__version__}.
            
            This bot can do several things. It can:
                - Add quest which will be presented as embeds
                - Allow you to set quests as complete, in progress, and failed
                - Allow you to view quest that were added
                - Set quest challenge ratings
                - And More
            
            Run !help to view this bot's syntax for commands. ```
            ''')

        break

#Bot leaves server
@client.event
async def on_guild_remove(guild):
    #Remove prefixes for bot
    with open('prefixes.json', 'r') as f:
        prefixes = json.load(f)

    prefixes.pop(str(guild.id))

    with open('prefixes.json', 'w') as f:
        json.dump(prefixes, f, indent=4)


    #Remove quest data
    db = sqlite3.connect('main.sqlite')
    cursor = db.cursor()
    cursor.execute(f'DELETE FROM quest_list WHERE guild_id = {guild.id}')

    db.commit()

    cursor.close()
    db.close()

########################################################################################################################
#   COMMANDS                                                                                                           #
########################################################################################################################

########################################################################################################################
#   TEST COMMANDS                                                                                                      #
########################################################################################################################

@client.command(aliases=['hi_world', 'hw', 'hello'])
async def hello_world(ctx):
    await ctx.send('Hello World! I am a bot!')

@client.command(aliases=['dcvers', 'codevers', 'apivers'])
async def discord_api_vers(ctx):
    await ctx.send(f'API Version: {discord.__version__}')

@client.command(aliases=['link', 'link_test', 'linktesting'])
async def send_link(ctx):
    await ctx.send('https://www.youtube.com/watch?v=Z7VNyregOtA')

@client.command(aliases=['test', 'test_embed', 'embed'])
async def embed_test(ctx):
    embed = discord.Embed(title='Test Embed',
                          description='This is a test embed example',
                          color=0x197d64)
    await ctx.send(embed=embed)


########################################################################################################################
#   Setup/Administrative Commands                                                                                      #
########################################################################################################################
@client.command()
@commands.has_guild_permissions(administrator=True)
async def changeprefix(ctx, prefix):
    with open('prefixes.json', 'r') as f:
        prefixes = json.load(f)

    prefixes[str(ctx.guild.id)] = prefix

    with open('prefixes.json', 'w') as f:
        json.dump(prefixes, f, indent=4)

    await ctx.send(f'```Prefix changed to {prefix}```')

#ERROR HANDLERS for prefix command
@changeprefix.error
async def prefixerror(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('The command is missing the correct arguments.\n```changeprefix [prefix]```')
    else:
        await ctx.send('An error has occurred!')

