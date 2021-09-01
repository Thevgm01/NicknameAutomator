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
favorites_user_ids = []
favorites_user_num = []
if favorites.cell(1, 1).value:
    favorites_user_ids = favorites.row_values(1)
    # TODO Have the sheet automatically count the number of entries and just steal that value
    favorites_user_num = favorites.row_values(2)
    # TODO Do this in more places
    for i in range(len(favorites_user_num)):
        favorites_user_num[i] = int(favorites_user_num[i])


def add_favorite(user_id, content):
    index = 0
    user_id = str(user_id)
    if user_id not in favorites_user_ids:
        index = len(favorites_user_ids)
        favorites_user_ids.append(user_id)
        favorites_user_num.append(0)
        favorites.update_cell(1, index + 1, user_id)
    else:
        index = favorites_user_ids.index(user_id)

    favorites_user_num[index] += 1
    favorites.update_cell(2, index + 1, favorites_user_num[index])
    favorites.update_cell(favorites_user_num[index] + 2, index + 1, content)
