import os
import json
from discord.ext import commands

import nickname_generator
import nickname_manager
import sheet_manager

bot = commands.Bot(command_prefix='!')


@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord and {len(bot.guilds)} guilds')


@bot.event
async def on_reaction_add(reaction, user):
    if user == bot.user:
        return

    #['⬅', '⭐', '❓', '➡']
    message = ""
    if reaction.emoji == '⬅':
        message = nickname_manager.get_prev(reaction.message.id)
    elif reaction.emoji == '⭐':
        content = message.content
        if '\n' in content:
            content = content.split('\n')[0]
        sheet_manager.add_favorite(user.id, content)
    elif reaction.emoji == '❓':
        message = nickname_manager.toggle_source(reaction.message.id)
    elif reaction.emoji == '➡':
        message = nickname_manager.get_next(reaction.message.id)

    if message:
        await reaction.message.edit(content=message)
        await reaction.remove(user)


# @bot.command(name='name', aliases=["n", "nick", "nickname"], help='Generates a random nickname')
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


@bot.command(name='name', aliases=["n", "nick", "nickname"], help='Generates a random nickname')
async def post_nickname_v2(ctx, *args):
    nickname = nickname_manager.Nickname()
    response = nickname.generate()
    message = await ctx.send(response)
    nickname_manager.remember(message.id, nickname)
    for reaction in ['⬅', '⭐', '❓', '➡']:
        await message.add_reaction(reaction)


@bot.command(name='refresh', help='Reloads the nickname info')
async def refresh(ctx, *args):
    data = sheet_manager.components.get_all_values()
    nickname_generator.set_data(data)
    await ctx.send("Data refreshed.")


def run():
    file = open("discord_credentials.json", 'r')
    json_file = json.load(file)
    token = json_file["token"]
    file.close()

    bot.run(token)
