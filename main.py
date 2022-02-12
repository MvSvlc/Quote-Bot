import asyncio
from datetime import datetime
import random
import time
import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

client = commands.Bot(command_prefix='!')
load_dotenv()

@client.event
async def on_ready():

    dir = 'Quotes'
    all_path = '{}/All'.format(dir)
    
    print('Checking for \'Quotes\' folder...')
    create_dir(dir)

    print('Attempting to create \'All\' folder...')
    create_dir(all_path)

    print('{0.user} is Online!'.format(client))

@client.command()
async def add(ctx, user='None' ,*args):
    timestr = time.strftime('%m%d%y %H%M%S')

    if len(args) < 1:
        await send_embed(ctx, ':x:\tUnable to process command\t:x:', '!add @user <quote>', discord.Color.red(), '', '')
        return

    await send_embed(ctx, ':repeat:\tAttempting to create quote...\t:repeat:', '', discord.Color.green(), '', '')
    await asyncio.sleep(3)
    
    removed_chars = '<@!>'
    for character in removed_chars:
        user = user.replace(character,'')

    try:
        user_object = await client.fetch_user(user)
    except (discord.errors.NotFound, discord.errors.HTTPException):
        await send_embed(ctx,':x:\tUnable to locate @{}\t:x:'.format(user), 'Must tag user', discord.Color.red(),'','')
        return

    user_str = str(user_object)

    def create_quote():
        dir = 'Quotes'
        quoted_user = user_str
        full_path = '{0}/{1}'.format(dir,quoted_user)
        all_path = '{}/All'.format(dir)

        print('Attempting to make directory: ' + full_path)
        create_dir(full_path)

        file_name = '{}.txt'.format(timestr)
        complete_file = os.path.join(full_path, file_name)
        all_file = os.path.join(all_path, file_name)
        print('Attempting to create quote file: ' + file_name)
        try:
            f = open(complete_file, 'x')
            all_f = open(all_file, 'x')
            print('[SUCCESS] Created quote:', file_name)
        except FileExistsError:
            print('[FAIL] Unable to create quote file...try again')

        content = ' '.join(args)
        f.write('{0}\n"{1}"'.format(quoted_user, content))
        all_f.write('{0}\n"{1}"'.format(quoted_user, content))

    create_quote()
    await send_embed(ctx, ':white_check_mark:\tSuccessfully created quote\t:white_check_mark:', '"{}"'.format(' '.join(args)), discord.Color.green(),'', '')

@client.command()
async def quote(ctx):
    all_path = 'Quotes/All'

    if len(os.listdir(all_path)) == 0:
        await send_embed(ctx, ':x:\tThere are currently no quotes stored!\t:x:', 'Try using !add to add new quotes', discord.Color.red(),'','')
        return

    rand_quote = random.choice(os.listdir(all_path))
    full_path = os.path.join(all_path, rand_quote)
    rand_file = open(full_path, 'r')
    created_user = rand_file.readline().rstrip('\n')

    file_name_extension= os.path.basename(full_path)
    file_name = os.path.splitext(file_name_extension)[0]

    member = await commands.MemberConverter().convert(ctx, created_user)

    file_content = rand_file.read()

    time_str = file_name.split(' ')
    time_obj = datetime.strptime(time_str[0], '%m%d%y')
    time_stamp = time_obj.strftime('%B %d, %Y')

    await send_embed(ctx, file_content,'', discord.Color.random(), member, member.avatar_url, time_stamp)

def create_dir(str):
    try:
        os.mkdir(str)
        print('[SUCCESS] Directory', str, 'created!')
    except FileExistsError:
        print('[INFO] Directory', str, 'exists - Continuing...')


async def send_embed(ctx, title, description, color, author, icon, footer=None):
    embed = discord.Embed(title = title,
    description = description,
    color = color)

    if footer is not None:
        embed.set_footer(text=footer)

    embed.set_author(name=author, icon_url=icon)
    await ctx.send(embed=embed)

client.run(os.getenv('TOKEN'))