import discord_bot
import nickname_generator
import sheet_manager

data = sheet_manager.components.get_all_values()
nickname_generator.set_data(data)
discord_bot.run()
