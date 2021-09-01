import gspread
from gspread import Cell
from oauth2client.service_account import ServiceAccountCredentials

import nickname_manager
import sheet_info

_scope = ["https://spreadsheets.google.com/feeds",
         "https://www.googleapis.com/auth/spreadsheets",
         "https://www.googleapis.com/auth/drive.file",
         "https://www.googleapis.com/auth/drive"]

_credentials = ServiceAccountCredentials.from_json_keyfile_name("google_credentials.json", _scope)
_client = gspread.authorize(_credentials)
_sheet = _client.open(sheet_info.SHEET_NAME)  # Open the spreadsheet

components = _sheet.worksheet("Components")

favorites_sheet = _sheet.worksheet("Favorites")
favorites_user_ids = []
favorites_user_num = []
if favorites_sheet.cell(1, 1).value:
    favorites_user_ids = favorites_sheet.row_values(1)
    # TODO Have the sheet automatically count the number of entries and just steal that value
    favorites_user_num = favorites_sheet.row_values(2)
    # TODO Do this in more places
    for i in range(len(favorites_user_num)):
        favorites_user_num[i] = int(favorites_user_num[i])


messages_sheet = _sheet.worksheet("Messages")
messages = []
seeds = []
if messages_sheet.cell(1, 1).value:
    messages = messages_sheet.col_values(1)
    seeds = messages_sheet.col_values(2)
    for i in range(len(messages)):
        nickname_manager.nicks[messages[i]] = nickname_manager.Nickname(int(seeds[i]))


def update_message_seed(message_id, seed):
    cells = []
    index = 0
    message_id = str(message_id)
    if message_id not in messages:
        index = len(messages)
        messages.append(message_id)
        seeds.append(seed)
        cells.append(Cell(row=index + 1, col=1, value=message_id))
    else:
        index = messages.index(message_id)

    cells.append(Cell(row=index + 1, col=2, value=seed))
    messages_sheet.update_cells(cells)


def add_favorite(user_id, content):
    cells = []
    index = 0
    user_id = str(user_id)
    if user_id not in favorites_user_ids:
        index = len(favorites_user_ids)
        favorites_user_ids.append(user_id)
        cells.append(Cell(row=1, col=index + 1, value=user_id))
        # TODO Also add the formula when adding a new user
    else:
        index = favorites_user_ids.index(user_id)

    favorites_user_num[index] += 1
    cells.append(Cell(row=favorites_user_num[index] + 2, col=index + 1, value=content))
    favorites_sheet.update_cells(cells)
