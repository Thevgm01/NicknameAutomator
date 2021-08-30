import discord_bot
import nickname_generator
import sheet_manager

data = sheet_manager.get_data()
nickname_generator.set_data(data)
discord_bot.run()
