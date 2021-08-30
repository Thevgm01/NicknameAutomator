import gspread
from oauth2client.service_account import ServiceAccountCredentials

import sheet_info

scope = ["https://spreadsheets.google.com/feeds",
         "https://www.googleapis.com/auth/spreadsheets",
         "https://www.googleapis.com/auth/drive.file",
         "https://www.googleapis.com/auth/drive"]

credentials = ServiceAccountCredentials.from_json_keyfile_name("google_credentials.json", scope)
client = gspread.authorize(credentials)
nickname_data = client.open(sheet_info.SHEET_NAME).sheet1  # Open the spreadsheet


def get_data():
    return nickname_data.get_all_values()
