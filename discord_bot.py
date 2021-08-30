import os
import json
from discord.ext import commands

import nickname_generator

token = None

with open("discord_credentials.json", 'r') as file:
    json = json.load(file)
    token = json["token"]

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
    bot.run(token)
