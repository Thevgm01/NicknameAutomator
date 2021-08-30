import discord_bot
import nickname_generator
import gspread
from oauth2client.service_account import ServiceAccountCredentials


scope = ["https://spreadsheets.google.com/feeds",
         "https://www.googleapis.com/auth/spreadsheets",
         "https://www.googleapis.com/auth/drive.file",
         "https://www.googleapis.com/auth/drive"]

credentials = ServiceAccountCredentials.from_json_keyfile_name("google_credentials.json", scope)
client = gspread.authorize(credentials)
sheet = client.open("Nickname Categorization").sheet1  # Open the spreadsheet
data = sheet.get_all_values()  # Get a list of all records

nickname_generator.set_data(data)
discord_bot.run()
