import gspread
from oauth2client.service_account import ServiceAccountCredentials

import sheet_info

_scope = ["https://spreadsheets.google.com/feeds",
         "https://www.googleapis.com/auth/spreadsheets",
         "https://www.googleapis.com/auth/drive.file",
         "https://www.googleapis.com/auth/drive"]

_credentials = ServiceAccountCredentials.from_json_keyfile_name("google_credentials.json", _scope)
_client = gspread.authorize(_credentials)
_sheet = _client.open(sheet_info.SHEET_NAME)  # Open the spreadsheet
components = _sheet.worksheet("Components")
favorites = _sheet.worksheet("Favorites")


favorites_users = []


class User:
    id = ""
    num = 0


def add_favorite(user_id, content):
    index = 0
    if user_id not in favorites_user_ids:
        index = len(favorites_user_ids)
        favorites_user_ids.append(user_id)
    else:
        index = favorites_user_ids