import os
import json
import time

import discord
from discord.ext import tasks, commands
from discord.ext.commands import has_permissions

import nickname_generator
import sheet_manager

# Bot / Change Nickname, Manage Nickname, Send Messages, Manage Messages, Read Message History, Add Reactions
# https://discord.com/api/oauth2/authorize?client_id=878364959447351296&permissions=201402432&scope=bot
from nickname import Nickname

bot = commands.Bot(command_prefix='!')


nicknames = {}
new_nicknames = []
changed_nicknames = []


@tasks.loop(seconds=5.0)
async def batch_update_sheet():
    global new_nicknames
    global changed_nicknames
    if new_nicknames or changed_nicknames:
        sheet_manager.update_message_seeds(new_nicknames, changed_nicknames)
        new_nicknames = []
        changed_nicknames = []


@bot.event
async def on_ready():
    print(bot.user.name + " has connected to Discord and " + str(len(bot.guilds)) + " guilds\nCurrently tracking " + str(len(nicknames)) + " messages")


@bot.event
async def on_raw_reaction_add(payload):
    dm = False
    msg_id = payload.message_id
    reaction = payload.emoji.name
    user = payload.member

    message_channel = bot.get_channel(payload.channel_id)

    if not message_channel or isinstance(message_channel, discord.channel.DMChannel):
        return

    target_message = await message_channel.fetch_message(msg_id)

    if user == bot.user:
        return

    if target_message.author != bot.user:
        return

    # print("Message %i was reacted to with %s" % (msg_id, reaction))

    # ['⬅', '⭐', '❓', '➡']
    if msg_id in nicknames:
        if not dm:
            await target_message.remove_reaction(payload.emoji, user)

        nickname = nicknames[msg_id]
        if reaction == '⬅':
            message = nickname.get_prev()
            if nickname not in changed_nicknames:
                changed_nicknames.append(nickname)
            await target_message.edit(content=message)
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
            if nickname not in changed_nicknames:
                changed_nicknames.append(nickname)
            await target_message.edit(content=message)
    # else:
        # print("Message %i not in tracked nicknames" % msg_id)


@bot.command(name='name', aliases=["n", "nick", "nickname"], help="Generates a random nickname\nType \'x#\' to generate that many nickanames\nType any sequence of letters to try and force it to apepar")
async def post_nickname(ctx, *args):
    start_time = time.time()

    num = 1
    force = ""
    force_attempts = 0
    force_attempt_limit = 50000
    char_limit = 2000
    for arg in args:
        if arg[0] == 'x':
            try:
                num = int(arg[1:])
            except ValueError:
                pass
        elif not force:
            if arg.startswith("acronym="):
                force = '(' + arg[8:].lower() + ')'
            else:
                force = arg.lower()
    response = ""

    nickname = Nickname()

    i = 0
    while i < num:
        cur = nickname.get_next()
        if force == "" or force in cur.lower():
            if len(response) + len(cur) >= char_limit:
                break
            response += cur + '\n'
            i += 1
        elif response == "":  # Track failures if nothing has come back successful yet
            if force_attempts >= force_attempt_limit:
                await ctx.send("I generated %s nicknames, but none of them had the string \"%s\"." % (force_attempt_limit, force))
                return
            force_attempts += 1
        if time.time() - start_time > 0.25:  # Display the typing indicator if this is taking too long
            await ctx.trigger_typing()
            start_time = time.time() + 9  # Trigger it again in 9 seconds, since trigger_typing() automatically stops after 10
    await ctx.send(response)


@bot.command(name='name2', aliases=["n2", "nick2", "nickname2", "forever"], help="Shows a message that you can react to with different commands")
async def post_nickname_v2(ctx, *args):
    nickname = Nickname()
    response = nickname.generate()
    message = await ctx.send(response)
    nickname.message_id = message.id
    nickname.message_row = len(nicknames) + 1
    nicknames[message.id] = nickname
    new_nicknames.append(nickname)
    for reaction in ['⬅', '⭐', '❓', '➡']:
        await message.add_reaction(reaction)
    await ctx.message.delete()


@bot.command(name='refresh', help='Reloads the nickname info')
@commands.has_permissions(administrator=True)
async def refresh(ctx, *args):
    await ctx.trigger_typing()

    global nicknames
    nicknames = sheet_manager.load_existing_messages()

    data = sheet_manager.components.get_all_values()
    nickname_generator.set_data(data)

    await ctx.send("Data refreshed.", delete_after=3)
    await ctx.message.delete()


@bot.command(name='kill', aliases=['stop', 'shutdown'], help='Stops the bot')
@commands.has_permissions(administrator=True)
async def kill(ctx):
    await ctx.send("Goodbye.")
    exit(1)


def run():
    file = open("discord_credentials.json", 'r')
    json_file = json.load(file)
    token = json_file["token"]
    file.close()

    batch_update_sheet.start()
    bot.run(token)
