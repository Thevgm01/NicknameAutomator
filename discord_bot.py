import os
import json
from discord.ext import tasks, commands

import nickname_generator
import sheet_manager

# Bot / Change Nickname, Manage Nickname, Send Messages, Manage Messages, Read Message History, Add Reactions
# https://discord.com/api/oauth2/authorize?client_id=878364959447351296&permissions=201402432&scope=bot
from nickname import Nickname

bot = commands.Bot(command_prefix='!')


nicknames = {}
changed_nicknames = []


@tasks.loop(seconds=2.0)
async def batch_update_sheet():
    global changed_nicknames
    sheet_manager.update_message_seeds(changed_nicknames)
    changed_nicknames = []


@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord and {len(bot.guilds)} guilds\nCurrently tracking {len(nicknames)} messages')


@bot.event
async def on_raw_reaction_add(payload):
    target_message = await bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
    msg_id = str(target_message.id)
    reaction = payload.emoji.name
    user = payload.member

    if user == bot.user:
        return

    # ['⬅', '⭐', '❓', '➡']
    # if msg_id in nickname_manager.nicks:
    if msg_id in nicknames:
        nickname = nicknames[msg_id]
        if reaction == '⬅':
            message = nickname.get_prev()
            await target_message.edit(content=message)
            changed_nicknames.append(nickname)
        elif reaction == '⭐':
            content = target_message.content
            if '\n' in content:
                content = content.split('\n')[0]
            sheet_manager.add_favorite(user.id, content)
        elif reaction == '❓':
            message = nickname.toggle_source()
            await target_message.edit(content=message)
        elif reaction == '➡':
            message = nickname.get_next()
            await target_message.edit(content=message)
            changed_nicknames.append(nickname)

        await target_message.remove_reaction(payload.emoji, user)


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
    nickname = Nickname()
    response = nickname.generate()
    message = await ctx.send(response)
    nicknames[message.id] = nickname
    sheet_manager.update_message_seed(message.id, nickname.seed())
    for reaction in ['⬅', '⭐', '❓', '➡']:
        await message.add_reaction(reaction)


@bot.command(name='refresh', help='Reloads the nickname info')
async def refresh(ctx, *args):
    global nicknames
    nicknames = sheet_manager.load_existing_messages()

    data = sheet_manager.components.get_all_values()
    nickname_generator.set_data(data)

    await ctx.send("Data refreshed.")


def run():
    file = open("discord_credentials.json", 'r')
    json_file = json.load(file)
    token = json_file["token"]
    file.close()

    batch_update_sheet.start()
    bot.run(token)
