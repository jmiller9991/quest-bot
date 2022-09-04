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

client.remove_command('help')
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

@client.command(aliases=['h'])
async def help(ctx, command=None):
    if command == None:
        await ctx.send('''
        ```
        Command List:
            - create_quest (alias cq)
            - quest_builder (alias qb)
            - edit_quest (alias eq)
            - view_quest (alias vq)
            - quest_list (alias ql)
            - delete_quest (alias dq)
            
        Type help <command> for the usage of the command
        ```
        ''')
    elif (command == 'create_quest' or command == 'cq'):
        await ctx.send('''
        ```
        create_quest title description author_name author_image_link reward_type quest_accepted_date quest_image_link quest_challenge
        where all things that are more than one word must be surrounded in quotes
        
        This will create the quest with the information you provide. The fields are described below.
        
        title is the quest title - required and cannot share the same title with another existing quest
        description is the description of the quest - required
        author_name is the name of the quest giver - required
        author_image_link is a link to the image of the quest giver - you can use a default image by typing default or none for no image
        reward_type is the text that describes what the players will get as a reward - required
        quest_accepted_date is the day the players took the quest - required
        quest_image_link is a link to the image related to the quest - you can use a default image by typing default or none for no image
        quest_challenge is the challenge level of the quest - this can only be \"none\", \"very easy\", \"easy\", \"medium\", \"hard\", or \"deadly\"
        ```
        ''')
    elif (command == 'quest_builder' or command == 'qb'):
        await ctx.send('''
        ```
        quest_builder
        
        This will provide you a step-by-step guide to build a quest.
        ```
        ''')
    elif (command == 'edit_quest' or command == 'eq'):
        await ctx.send('''
        ```
        edit_quest field_to_change value
        where all things that are more than one word must be surrounded in quotes
        
        This will change the field you enter in the command to the value you enter in the command. The field's are described below.
        
        field_to_change is the thing you want to change in the quest and value is the value that you are changing it too - this must be one of the phrases listed below, and value restrictions are included
            - title => quest title - cannot share the same title with another existing quest
            - description => quest description
            - author_name => quest giver name
            - author_image_link => link to the image of the quest giver - can use a default image by typing default or none for no image as value
            - reward_type => text that describes what the players will get as a reward
            - quest_accepted_date => day the players took the quest
            - quest_image_link => link to the image related to the quest - can use a default image by typing default or none for no image as value
            - quest_challenge => challenge level of the quest - value must be \"none\", \"very easy\", \"easy\", \"medium\", \"hard\", or \"deadly\"
        ```
        ''')
    elif (command == 'view_quest' or command == 'vq'):
        await ctx.send('''
        ```
        view_quest quest_title
        where all things that are more than one word must be surrounded in quotes
        
        quest_title is the title of the quest you want to view
        ```
        ''')
    elif (command == 'quest_list' or command == 'ql'):
        await ctx.send('''
        ```
        quest_list
        
        This list the titles of all quest you have created, sorted by in-progress, complete, and failed.
        ```
        ''')
    elif (command == 'delete_quest' or command == 'dq'):
        await ctx.send('''
        ```
        delete_quest quest_title
        where all things that are more than one word must be surrounded in quotes
        
        quest_title is the title of the quest you want to delete
        ```
        ''')

########################################################################################################################
#   Setup/Administrative Commands                                                                                      #
########################################################################################################################
# changes prefix
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

########################################################################################################################
#   Quest Commands                                                                                                     #
########################################################################################################################
# create quest
@client.command(aliases=['cq'])
@commands.has_guild_permissions(administrator=True)
async def create_quest(ctx, title, desc, author_name, author_image, reward_type, quest_accepted_date, quest_image, quest_challenge):
    await ctx.send('Error')