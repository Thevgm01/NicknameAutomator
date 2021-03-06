import gspread
from gspread import Cell
from oauth2client.service_account import ServiceAccountCredentials

import sheet_info
from nickname import Nickname

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


def load_existing_messages():
    nicknames = {}
    if messages_sheet.cell(1, 1).value:
        message_ids = messages_sheet.col_values(1)
        seeds = messages_sheet.col_values(2)
        for i in range(len(message_ids)):
            msg_id = int(message_ids[i])
            seed = int(seeds[i])
            # print("Loading tracked message %i" % msg_id)
            nickname = Nickname(seed)
            nickname.message_id = msg_id
            nickname.message_row = i + 1
            nicknames[msg_id] = nickname
    return nicknames


def update_message_seeds(new_nicknames, changed_nicknames):
    cells = []
    for nickname in new_nicknames:
        cells.append(Cell(row=nickname.message_row, col=sheet_info.NICKNAME_MESSAGE_ID_COL, value=str(nickname.message_id)))
        cells.append(Cell(row=nickname.message_row, col=sheet_info.NICKNAME_MESSAGE_SEED_COL, value=str(nickname.seed())))
    for nickname in changed_nicknames:
        cells.append(Cell(row=nickname.message_row, col=sheet_info.NICKNAME_MESSAGE_SEED_COL, value=str(nickname.seed())))
    if cells:
        messages_sheet.update_cells(cells)


def add_favorite(user_id, content):
    cells = []
    index = 0
    user_id = str(user_id)
    if user_id not in favorites_user_ids:
        index = len(favorites_user_ids)
        favorites_user_ids.append(user_id)
        cells.append(Cell(row=1, col=index + 1, value=str(user_id)))
        # TODO Also add the formula when adding a new user
    else:
        index = favorites_user_ids.index(user_id)

    favorites_user_num[index] += 1
    cells.append(Cell(row=favorites_user_num[index] + 2, col=index + 1, value=content))
    favorites_sheet.update_cells(cells)
