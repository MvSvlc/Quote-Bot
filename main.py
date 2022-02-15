import asyncio
from datetime import datetime
import os
import sqlite3
import discord
from discord.ext import commands
from configparser import ConfigParser
from dotenv import load_dotenv

client = commands.Bot(command_prefix='!')
cfg = ConfigParser()
cfg.read('config.ini')
load_dotenv()

def create_connection(db_file):
    conn = None
    try:
        print('[INFO] Attempting to connect to DB...')
        conn = sqlite3.connect(db_file)
        print('[SUCCESS] Connected to DB...')
        return conn
    except sqlite3.Error as error:
        print('[ERROR] Error connecting to DB -', error)
    
    return conn

def create_table(conn, create_table_sql):
    try:
        cursor = conn.cursor()
        cursor.execute(create_table_sql)
    except sqlite3.Error as error:
        print('[ERROR] Unable to create table -', error)

def create_insert_sql(conn, name, quote):
    try:
        c = conn.cursor()
        sql = f'INSERT INTO quotes(name, quote, create_date) VALUES (\'{name}\', \'{quote}\', DATE(\'now\'));'
        c.execute(sql)
        conn.commit()
    except sqlite3.Error as error:
        print('[ERROR] Unable to insert into table - ', error)

database_name = cfg.get('database','Name')
database = rf'{database_name}.db'
sql_create_quotes_table = ''' CREATE TABLE IF NOT EXISTS quotes (
    id INTEGER PRIMARY KEY,
    name text NOT NULL,
    quote text NOT NULL,
    create_date text NOT NULL); '''



conn = create_connection(database)

if conn is not None:
    create_table(conn, sql_create_quotes_table)
else:
    print('[ERROR] Unable to create database connection')


@client.event
async def on_ready():

    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name='all your thoughts'))

    print('{0.user} is Online!'.format(client))

@client.command()
async def add(ctx, user='None' ,*args):

    if len(args) < 1:
        await send_embed(ctx, ':x:\tUnable to process command\t:x:', '!add @user <quote>', discord.Color.red(), '', '')
        print('[ERROR] Not enough arguments supplied')
        return

    print('[INFO] Attempting to create new quote...')
    await send_embed(ctx, ':repeat:\tAttempting to create quote...\t:repeat:', '', discord.Color.teal(), '', '')
    await asyncio.sleep(3)
    
    removed_chars = '<@!>'
    for character in removed_chars:
        user = user.replace(character,'')

    try:
        user_object = await client.fetch_user(user)
    except (discord.errors.NotFound, discord.errors.HTTPException):
        await send_embed(ctx,':x:\tUnable to locate @{}\t:x:'.format(user), 'Must tag user', discord.Color.red(),'','')
        print('[ERROR] Unable to located user')
        return

    user_str = str(user_object)


    content = ' '.join(args)
    create_insert_sql(conn, user_str, content)

    await send_embed(ctx, ':white_check_mark:\tSuccessfully created quote\t:white_check_mark:', '"{}"'.format(' '.join(args)), discord.Color.green(),'', '')
    print(f'[SUCCESS] Inserted new quote to DB - @{user_str}: \'{content}\'')

@client.command()
async def quote(ctx):

    print('[INFO] Attempting to retrieve quote...')
    sql_object = get_rand_sql(conn)
    if sql_object is None:
        await send_embed(ctx, ':x:\tThere are currently no quotes stored!\t:x:', 'Try using !add to add new quotes', discord.Color.red(),'','')
        print('[ERROR] Unable to retrieve quote')
        return

    user = sql_object.name
    content = sql_object.quote
    date = sql_object.date

    member = await commands.MemberConverter().convert(ctx, user)

    time_obj = datetime.strptime(date, '%Y-%m-%d')
    time_stamp = time_obj.strftime('%B %d, %Y')

    await send_embed(ctx, content,'', discord.Color.random(), member.display_name, member.avatar_url, time_stamp)
    print(f'[SUCCESS] Successfully retrieved quote - @{member.display_name}: \'{content}\'')

def get_rand_sql(conn):
    class SQL(object):
        pass
    sql_object = SQL()

    try:
        c = conn.cursor()
        sql = 'SELECT * FROM quotes ORDER BY RANDOM() LIMIT 1;'
        c.execute(sql)
        result = c.fetchone()
        if result is None:
            return None
        sql_object.name = result[1]
        sql_object.quote = result[2]
        sql_object.date = result[3]
        return sql_object
    except sqlite3.Error as error:
        print('[ERROR] Unable to retrieve random quote -', error)
        return None


async def send_embed(ctx, title, description, color, author, icon, footer=None):
    embed = discord.Embed(title = title,
    description = description,
    color = color)

    if footer is not None:
        embed.set_footer(text=footer)

    embed.set_author(name=author, icon_url=icon)
    await ctx.send(embed=embed)

client.run(os.environ.get('TOKEN'))
