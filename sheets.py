import random
import gspread
from oauth2client.service_account import ServiceAccountCredentials


class Plurality:
    ANY = 0
    SINGULAR = 1
    PLURAL = 2


vowels = ['a', 'e', 'i', 'o', 'u', 'y']


def isVowel(letter):
    letter = letter.lower()
    for v in vowels:
        if v is letter:
            return True
    return False


def isConsonant(letter):
    return not isVowel(letter)


def mapLetter(letter):
    return ord(letter.upper()) - ord('A')


def getRandomCoordsFixed(cols):
    randRow = random.randrange(0, numRows - 1) + rowOffset
    randCol = random.choice(cols)
    if type(randCol) is str:
        randCol = mapLetter(randCol)
    return [randRow, randCol]


def getRandomCoords(*cols):
    return getRandomCoordsFixed(cols)


def getRandomEntry(*cols):
    coords = getRandomCoordsFixed(cols)
    return data[coords[0]][coords[1]]


def generateNickname():
    components = []
    subjectPlurality = ""
    # Any subject, don't proceed until one is found
    while not components:
        coords = getRandomCoords('M', 'N', 'O')
        entry = data[coords[0]][coords[1]]
        if entry:
            components.append(entry)
            if coords[1] == ord('M'):
                subjectPlurality = Plurality.ANY
            elif coords[1] == ord('N'):
                subjectPlurality = Plurality.SINGULAR
            else:
                subjectPlurality = Plurality.PLURAL
    print(subjectPlurality)
    # Get pre-subject
    entry = getRandomEntry('L')
    if entry:
        components[0] = entry + components[0]
    # Descriptors
    descriptors = []
    while True:
        coords = getRandomCoords('I', 'J')
        entry = data[coords[0]][coords[1]]
        if entry and coords[1] == ord('I'):
            entry = getRandomEntry('H') + entry + getRandomEntry('K')
            descriptors.append(entry)
        else:
            if entry:
                descriptors.append(entry)
            break
    components = descriptors + components
    # Curse
    entry = getRandomEntry('G')
    if entry:
        components.insert(0, entry)
    # Quantity
    entry = getRandomEntry('F')
    if entry and subjectPlurality != Plurality.SINGULAR:
        components.insert(0, entry)
    # Pre Everything
    if subjectPlurality == Plurality.SINGULAR:
        entry = getRandomEntry('D', 'E')
    else:
        entry = getRandomEntry('D')
    if entry:
        components.insert(0, entry)
    # Post Subject
    # TODO FIX
    lastIsVowel = isVowel(components[-1][-1])
    if subjectPlurality != Plurality.PLURAL:
        coords = getRandomCoords('P', 'R')
    else:
        coords = getRandomCoords('P', 'Q')
    entry = data[coords[0]][coords[1]]
    if entry:
        if lastIsVowel and coords[1] == ord('Q') and data[coords[0]][coords[1] + 1]:
            entry = data[coords[0]][coords[1] + 1]
        components[-1] = components[-1] + entry
    # Modifier
    entry = getRandomEntry('T')
    if entry:
        components.append(entry)
    # Post Everything
    entry = getRandomEntry('U')
    if entry:
        components.append(entry)

    # TODO Replace all double spaces with single spaces
    # TODO Make sure the same word can't appear more than once
    # TODO Multiple subjects
    # TODO Fix bias with selecting individual items from different columns
    #      (calculate a ratio of filled-to-unfilled cells for each column)
    # TODO Make the | separator work
    result = " ".join(components)
    return result


scope = ["https://spreadsheets.google.com/feeds",
         "https://www.googleapis.com/auth/spreadsheets",
         "https://www.googleapis.com/auth/drive.file",
         "https://www.googleapis.com/auth/drive"]

credentials = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)

client = gspread.authorize(credentials)

sheet = client.open("Nickname Categorization").sheet1  # Open the spreadhseet

data = sheet.get_all_values()  # Get a list of all records

rowOffset = 1
colOffset = 2
numRows = len(data) - rowOffset
numCols = len(data[0]) - colOffset

i = 0
while i < 20:
    nickname = generateNickname()
    print(nickname)
    i += 1
