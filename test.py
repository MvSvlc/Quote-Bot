import asyncio
import random
import sys
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
async def add(ctx, *args):
    if len(args) < 1:
        await ctx.send('Please supply more arguments')
        return

    message = await ctx.send('Attempting to create quote...')
    

    def create_quote():
        timestr = time.strftime('%Y%m%d-%H%M%S')
        dir = 'Quotes'
        user_name = '{0.author}'.format(ctx)
        full_path = '{0}/{1}'.format(dir,user_name)
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
        f.write('{}'.format(content))
        all_f.write('{}'.format(content))

    create_quote()
    message.edit(content='Sucessfully created quote: {}'.format(args))

@client.command()
async def quote(ctx):
    all_path = 'Quotes/All'
    rand_quote = random.choice(os.listdir(all_path))
    full_path = os.path.join(all_path, rand_quote)
    rand_file = open(full_path, 'r')

    file_content = rand_file.read()
    
    embed = discord.Embed(
        title = '{}'.format(file_content),
        color = discord.Color.random()
    )
    await ctx.send(embed=embed)

def create_dir(str):
    try:
        os.mkdir(str)
        print('[SUCCESS] Directory', str, 'created!')
    except FileExistsError:
        print('[INFO] Directory', str, 'exists - Continuing...')

client.run(os.getenv('TOKEN'))