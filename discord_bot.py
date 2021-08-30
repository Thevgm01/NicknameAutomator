import os
import json
from discord.ext import commands

import nickname_generator
import sheet_manager

bot = commands.Bot(command_prefix='!')


@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord and {len(bot.guilds)} guilds')


@bot.command(name='name', aliases=["n", "nick", "nickname"], help='Generates a random nickname')
async def post_nickname(ctx, *args):
    num = 1
    force = ""
    attempts = 0
    limit = 10000
    for arg in args:
        if arg[0] == 'x':
            try:
                num = int(arg[1:])
            except ValueError:
                pass
        else:
            force = arg.lower()
    response = ""
    i = 0
    while i < num:
        cur = nickname_generator.generate_nickname()
        if force == "" or force in cur.lower():
            response += cur + '\n'
            i += 1
        elif response == "":  # Track failures if nothing has come back successful yet
            if attempts >= limit:
                await ctx.send("I generated %s nicknames, but none of them had the string \"%s\"." % (limit, force))
                return
            attempts += 1
    await ctx.send(response)


@bot.command(name='refresh', help='Reloads the nickname info')
async def post_nickname(ctx, *args):
    nickname_generator.set_data(sheet_manager.get_data())
    await ctx.send("Data refreshed.")


def run():
    file = open("discord_credentials.json", 'r')
    json_file = json.load(file)
    token = json_file["token"]
    file.close()

    bot.run(token)
