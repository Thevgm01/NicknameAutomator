import os
import json
from discord.ext import commands

import nickname_generator

bot = commands.Bot(command_prefix='!')


@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')


@bot.command(name='name', help='Generates a random nickname')
async def post_nickname(ctx):
    response = ""
    while response == "":
        response = nickname_generator.generate_nickname()
    await ctx.send(response)


def run():
    file = open("discord_credentials.json", 'r')
    json_file = json.load(file)
    token = json_file["token"]
    file.close()

    bot.run(token)
