import os
import discord
import json
from discord.ext import commands
from discord_slash import SlashCommand
import sqlite3
import asyncio


# JSON Prefixes
async def get_prefix(client, message):
    with open('prefixes.json', 'r') as f:
        prefixes = json.load(f)

    return prefixes[str(message.guild.id)]

client = commands.Bot(command_prefix=(get_prefix))

client.remove_command('help')
slash = SlashCommand(client, sync_commands=True)
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
        )
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
@slash.slash(name='hello_world', description="Hello World Command")
async def hello_world(ctx):
    await ctx.send('Hello World! I am a bot!')

@slash.slash(name='discord_api_vers', description='Show API Version')
async def discord_api_vers(ctx):
    await ctx.send(f'API Version: {discord.__version__}')

@slash.slash(name='send_link', description='link test')
async def send_link(ctx):
    await ctx.send('https://www.youtube.com/watch?v=Z7VNyregOtA')

@slash.slash(name='embed_test', description='embed testing')
async def embed_test(ctx):
    embed = discord.Embed(title='Test Embed',
                          description='This is a test embed example',
                          color=0x197d64)

    embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)

    await ctx.send(embed=embed)

@slash.slash(name='help', description="This will show help, you can include the string for each command")
async def help(ctx, command=None):
    if command is None:
        await ctx.send('''
        ```
        Command List:
            - create_quest
            - quest_builder
            - edit_quest
            - view_quest
            - quest_list
            - delete_quest
            - quest_status
            
        Type help <command> for the usage of the command
        ```
        ''')
    elif (command == 'create_quest'):
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
    elif (command == 'quest_builder'):
        await ctx.send('''
        ```
        quest_builder
        
        This will provide you a step-by-step guide to build a quest.
        ```
        ''')
    elif (command == 'edit_quest'):
        await ctx.send('''
        ```
        edit_quest quest_title field_to_change value
        where all things that are more than one word must be surrounded in quotes
        
        This will change the field you enter in the command to the value you enter in the command. The field's are described below.
        
        quest_title is the quest you want to change a value of
        
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
    elif (command == 'view_quest'):
        await ctx.send('''
        ```
        view_quest quest_title
        where all things that are more than one word must be surrounded in quotes
        
        quest_title is the title of the quest you want to view
        ```
        ''')
    elif (command == 'quest_list'):
        await ctx.send('''
        ```
        quest_list
        
        This list the titles of all quest you have created, sorted by in-progress, complete, and failed.
        ```
        ''')
    elif (command == 'delete_quest'):
        await ctx.send('''
        ```
        delete_quest quest_title
        where all things that are more than one word must be surrounded in quotes
        
        quest_title is the title of the quest you want to delete
        ```
        ''')
    elif (command == 'quest_status'):
        await ctx.send('''
        ```
        quest_status quest_title status 
        where all things that are more than one word must be surrounded in quotes
        
        quest_title is the title of the quest you want to change the status of
        status is the status you are going to change the quest to - these can be in progress, complete, or failed
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
@slash.slash(name='create_quest', description='This will allow you to create a quest given certain information')
@commands.has_guild_permissions(administrator=True)
async def create_quest(ctx, title, desc, author_name, author_image, reward_type, quest_accepted_date, quest_image, quest_challenge):
    db = sqlite3.connect('main.sqlite')
    cursor = db.cursor()

    cursor.execute(f'SELECT quest_title FROM quest_list WHERE guild_id = {ctx.guild.id} AND quest_title = {title}')
    result = cursor.fetchone()

    if result is None:
        quest_title = title
    else:
        await ctx.send(f'{title} matches a provided title. Failing...')
        return

    quest_desc = desc
    quest_author = author_name
    quest_author_image = author_image
    quest_reward_type = reward_type
    quest_date = quest_accepted_date
    quest_img = quest_image

    if (quest_challenge is 'none' or quest_challenge is 'very easy' or quest_challenge is 'easy'
            or quest_challenge is 'medium' or quest_challenge is 'hard' or quest_challenge is 'deadly'):
        challenge = quest_challenge
    else:
        await ctx.send(f'{quest_challenge} is not an acceptable challenge level. Failing...')
        return

    cursor.execute(f'SELECT COUNT(quest_number) FROM quest_list WHERE guild_id = {ctx.guild.id}')
    result2 = cursor.fetchone()

    if result2 is None:
        quest_number = 0
    else:
        quest_number = result2[0] + 1

    vals = (ctx.guild.id, quest_number, quest_title, quest_desc, quest_author, quest_author_image, quest_reward_type, quest_date, quest_img, challenge, 'in progress')
    sql = (f'INSERT INTO quest_list(guild_id, quest_number, quest_title, quest_description, author_name, author_image, reward_type, quest_accepted_date, quest_image, quest_challenge, quest_status) VALUES(?,?,?,?,?,?,?,?,?,?,?)')

    cursor.execute(sql, vals)
    db.commit()

    prefix = get_prefix(client, ctx.message)

    await ctx.send(f'Quest Created. Do {prefix}view_quest {quest_title} to view this quest.')

    cursor.close()
    db.close()

@create_quest.error
async def cqerror(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f'The command is missing the correct arguments.\n```{get_prefix(client, ctx.message)}create_quest [title] [description] [author_name] [author_image_link] [reward_type] [quest_accepted_date] [quest_image_link] [quest_challenge]```')
    else:
        await ctx.send('An error has occurred!')


#edits a quest
@slash.slash(name='edit_quest', description='This will allow you to edit a quest given its name, field to change, and value to change.')
@commands.has_guild_permissions(administrator=True)
async def edit_quest(ctx, quest_title, field_to_change, value):
    db = sqlite3.connect('main.sqlite')
    cursor = db.cursor()

    cursor.execute(f'SELECT quest_title FROM quest_list WHERE guild_id = {ctx.guild.id} AND quest_title = {quest_title}')
    result = cursor.fetchone()

    if result is None:
        await ctx.send('This quest does not exist, failing...')
        return

    if field_to_change is 'title':

        cursor.execute(f'SELECT quest_title FROM quest_list WHERE guild_id = {ctx.guild.id} AND quest_title = {value}')
        result2 = cursor.fetchone()

        if result2 is not None:
            await ctx.send(f'{value} is already a quest name, failing...')
            return
        else:
            field = 'quest_title'

    elif field_to_change is 'description':
        field = 'quest_description'
    elif field_to_change is 'author_name':
        field = 'author_name'
    elif field_to_change is 'author_image_link':
        field = 'author_image'
    elif field_to_change is 'reward_type':
        field = 'reward_type'
    elif field_to_change is 'quest_accepted_date':
        field = 'quest_accepted_date'
    elif field_to_change is 'quest_image_link':
        field = 'quest_image'
    elif field_to_change is 'quest_challenge':
        if (value is 'none' or value is 'very easy' or value is 'easy' or value is 'medium' or value is 'hard' or value is 'deadly'):
            field = 'quest_challenge'
        else:
            await ctx.send(f'{value} is not acceptable for \"quest_challenge\" field, failing...')
            return
    else:
        await ctx.send(f'{field_to_change} is not acceptable, failing...')
        return

    cursor.execute(f'UPDATE quest_list SET {field} = {value} WHERE guild_id = {ctx.guild.id} AND quest_title = {quest_title}')

    db.commit()

    prefix = get_prefix(client, ctx.message)

    await ctx.send(f'Quest updated. Do {prefix}view_quest {quest_title} to view this quest.')

    cursor.close()
    db.close()
@edit_quest.error
async def eqerror(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f'The command is missing the correct arguments.\n```{get_prefix(client, ctx.message)}edit_quest [quest_title] [field_to_change] [value]``')
    else:
        await ctx.send('An error has occurred!')

# view a quest
@slash.slash(name='view_quest', description='This will allow you to view a quest given a title.')
async def view_quest(ctx, quest_title):
    db = sqlite3.connect('main.sqlite')
    cursor = db.cursor()

    #                        0               1                   2           3              4               5                  6            7               8
    cursor.execute(f'SELECT quest_title, quest_description, author_name, author_image, reward_type, quest_accepted_date, quest_image, quest_challenge, quest_status FROM quest_list WHERE guild_id = {ctx.guild.id} AND quest_title = {quest_title}')
    result = cursor.fetchone()

    if result is None:
        await ctx.send('This quest does not exist, failing...')
        return

    if result[7] is 'none':
        color1 = 0xB4B4B4
    elif result[7] is 'very easy':
        color1 = 0x30E200
    elif result[7] is 'easy':
        color1 = 0x156300
    elif result[7] is 'medium':
        color1 = 0xDFA300
    elif result[7] is 'hard':
        color1 = 0xFF0000
    elif result[7] is 'deadly':
        color1 = 0x6E0000
    else:
        color1 = 0xFFFFFF

    embed = discord.Embed(title=result[0],
                          description=result[1],
                          color=color1)

    if result[3].casefold() is 'none':
        embed.set_author(name=result[2])
    elif result[3].casefold() is 'default':
        file = discord.File("anonauthor.png")
        embed.set_author(name=result[2], icon_url="attachment://anonauthor.png")
    else:
        embed.set_author(name=result[2], icon_url=result[3])

    embed.add_field(name='Reward', value=result[4], inline=True)
    embed.add_field(name='Quest Accepted Date', value=result[5], inline=True)

    if result[6].casefold() is not 'none':
        embed.set_image(url=result[6])
    elif result[6].casefold() is 'default':
        file2 = discord.File("defaultimg.png")
        embed.set_image(url="attachment://defaultimg.png")

    embed.set_footer(text=result[8])

    await ctx.send(embed=embed)

    cursor.close()
    db.close()
@view_quest.error
async def vqerror(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f'The command is missing the correct arguments.\n```{get_prefix(client, ctx.message)}view_quest [quest_title]``')
    else:
        await ctx.send('An error has occurred!')

@slash.slash(name='quest_list', description='This will list all of the quest by their completion status.')
async def quest_list(ctx):
    db = sqlite3.connect('main.sqlite')
    cursor = db.cursor()

    complete = []
    in_progress = []
    failed = []

    for row in cursor.execute(f'SELECT quest_title, quest_status FROM quest_list WHERE guild_id = {ctx.guild.id}'):
        if row[1].casefold() is 'in progress':
            in_progress.append(row[0])
        elif row[1].casefold() is 'complete':
            complete.append(row[0])
        elif row[1].casefold() is 'failed':
            failed.append(row[0])
        else:
            print('error with information')

    await ctx.send('**--QUEST IN PROGRESS--**')
    for x in in_progress:
        await ctx.send(x)

    await ctx.send('**--QUEST COMPLETE--**')
    for x in complete:
        await ctx.send(x)

    await ctx.send('**--QUEST FAILED--**')
    for x in failed:
        await ctx.send(x)

    cursor.close()
    db.close()

@slash.slash(name='delete_quest', description='This will delete a quest given a name.')
@commands.has_guild_permissions(administrator=True)
async def delete_quest(ctx, quest_title):
    db = sqlite3.connect('main.sqlite')
    cursor = db.cursor()

    cursor.execute(f'SELECT quest_title FROM quest_list WHERE guild_id = {ctx.guild.id} AND quest_title = {quest_title}')
    result = cursor.fetchone()

    if result is None:
        await ctx.send('This quest does not exist, failing...')
        return

    cursor.execute(f'DELETE FROM quest_list WHERE guild_id = {ctx.guild.id} AND quest_title={quest_title}')

    db.commit()
    cursor.close()
    db.close()
@delete_quest.error
async def dqerror(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f'The command is missing the correct arguments.\n```{get_prefix(client, ctx.message)}delete_quest [quest_title]``')
    else:
        await ctx.send('An error has occurred!')

@client.command(aliases=['qs'])
@commands.has_guild_permissions(administrator=True)
async def quest_status(ctx, quest_title, status):
    db = sqlite3.connect('main.sqlite')
    cursor = db.cursor()

    cursor.execute(f'SELECT quest_title FROM quest_list WHERE guild_id = {ctx.guild.id} AND quest_title = {quest_title}')
    result = cursor.fetchone()

    if result is None:
        await ctx.send('This quest does not exist, failing...')
        return

    if (status is 'in progress' or status is 'complete' or status is 'failed'):
        sql = ('UPDATE quest_list SET quest_status = ? WHERE guild_id = ? AND quest_title = ?')
        vals = (status, ctx.guild.id, quest_title)

        cursor.execute(sql, vals)
    else:
        await ctx.send(f'{status} is not accepted. Failing...')
        return

    db.commit()
    cursor.close()
    db.close()
@quest_status.error
async def qserror(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f'The command is missing the correct arguments.\n```{get_prefix(client, ctx.message)}quest_status [quest_title] [status]``')
    else:
        await ctx.send('An error has occurred!')

@slash.slash(name='quest_builder', description='This will be a step-by-step guide for building a quest.')
@commands.has_guild_permissions(administrator=True)
async def quest_builder(ctx):
    db = sqlite3.connect('main.sqlite')
    cursor = db.cursor()

    def check(amsg):
        return amsg.author == ctx.author and amsg.channel == ctx.channel

    await ctx.send('''
    ```
    This is the quest builder. This will give you a step-by-step guide on building a quest.
    
    Let's first start with giving your quest a title. This title cannot match any quest titles that exist on the database. This includes complete and failed quest.
    ```
    ''')

    wait1 = True

    while(wait1):
        title = await client.wait_for("message", check=check)

        cursor.execute(
            f'SELECT quest_title FROM quest_list WHERE guild_id = {ctx.guild.id} AND quest_title = {title}')
        result = cursor.fetchone()

        if result is not None:
            await ctx.send('This quest does exist. Try again!')
            wait1 = True
        else:
            wait1 = False

    await ctx.send('''
    ```
    Good! Now let's get the description of the quest. 
    ```
    ''')

    desc = await client.wait_for("message", check=check)

    await ctx.send('''
    ```
    Good! Let's give the quest an author. This is the quest giver.
    ``` 
    ''')

    auth_name = await client.wait_for("message", check=check)

    await ctx.send('''
    ```
    Let's pick an image for the quest giver. If you do not want an image, write \"none\" exactly as written here. If you want to use a default image, type \"default\" exactly as written here.
    ``` 
    ''')

    auth_img = await client.wait_for("message", check=check)

    if (auth_img.casefold() is 'none'):
        author_image = 'none'
    elif (auth_img.casefold() is 'default'):
        author_image = 'default'
    else:
        author_image = auth_img

    await ctx.send('''
    ```
    Now, let's provide the reward. This can be anything you want it to be.
    ```
    ''')

    reward = await client.wait_for("message", check=check)

    await ctx.send('''
    ```
    Good job! Now, let's set the date the players accepted the quest. This can be today's date, the in-game date, etc.
    ```
    ''')

    quest_date = await client.wait_for("message", check=check)

    await ctx.send('''
    ```
    Great! Now, let's set the quest image. If you do not want an image, write \"none\" exactly as written here. If you want to use a default image, type \"default\" exactly as written here.
    ```
    ''')

    quest_img = await client.wait_for("message", check=check)

    if (quest_img.casefold() is 'none'):
        quest_image = 'none'
    elif (quest_img.casefold() is 'default'):
        quest_image = 'default'
    else:
        quest_image = quest_img

    await ctx.send('''
    ```
    Great job! Now, let's set the quest challenge level. This can only be \"none\", \"very easy\", \"easy\", \"medium\", \"hard\", or \"deadly\"
    ```
    ''')

    wait2 = True
    while(wait2):
        chal = await client.wait_for("message", check=check)

        if (chal is 'none' or chal is 'very easy' or chal is 'easy' or chal is 'medium' or chal is 'hard' or chal is 'deadly'):
            challenge = chal
            wait2 = False
        else:
            await ctx.send('This is not correct! Try again!')
            wait2 = True

    cursor.execute(f'SELECT COUNT(quest_number) FROM quest_list WHERE guild_id = {ctx.guild.id}')
    result2 = cursor.fetchone()

    if result2 is None:
        quest_number = 0
    else:
        quest_number = result2[0] + 1

    vals = (ctx.guild.id, quest_number, title, desc, auth_name, author_image, reward,
            quest_date, quest_image, challenge, 'in progress')
    sql = (
        f'INSERT INTO quest_list(guild_id, quest_number, quest_title, quest_description, author_name, author_image, reward_type, quest_accepted_date, quest_image, quest_challenge, quest_status) VALUES(?,?,?,?,?,?,?,?,?,?,?)')

    cursor.execute(sql, vals)

    db.commit()
    prefix = get_prefix(client, ctx.message)

    await ctx.send(f'**Congratulations!** The quest has been created. Type {prefix}view_quest {title} to view this quest.')

    cursor.close()
    db.close()

########################################################################################################################
#   OTHER IMPORTANT CODE                                                                                               #
########################################################################################################################

client.run('Token')