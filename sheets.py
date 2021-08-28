import random
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from titlecase import titlecase


class Plurality:
    ANY = 0
    SINGULAR = 1
    PLURAL = 2


vowels = ['a', 'e', 'i', 'o', 'u', 'y']


def isVowel(letter):
    letter = letter.lower()
    for v in vowels:
        if v == letter:
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
    return getEntry(coords)


def getEntry(coords):
    entry = data[coords[0]][coords[1]]
    if '|' in entry:
        entries = entry.split('|')
        return random.choice(entries)
    else:
        return entry


def generateNickname():
    entry = ""
    components = []
    componentsAdded = 0
    subjectPlurality = -1
    subjectEndsInVowel = False

    # Any subject, don't proceed until one is found
    while not components:
        coords = getRandomCoords('M', 'N', 'O')
        entry = getEntry(coords)
        if entry:
            components.append(entry)
            if coords[1] == ord('M') - ord('A'):
                subjectPlurality = Plurality.ANY
            elif coords[1] == ord('N') - ord('A'):
                subjectPlurality = Plurality.SINGULAR
            elif coords[1] == ord('O') - ord('A'):
                subjectPlurality = Plurality.PLURAL
            subjectEndsInVowel = isVowel(entry[-1])

    # Pre Subject
    entry = getRandomEntry('L')
    if entry:
        components[0] = entry + components[0]
        componentsAdded += 1

    # Descriptors
    descriptors = []
    while True:
        coords = getRandomCoords('I', 'J')
        entry = getEntry(coords)
        if entry and coords[1] == ord('I'):
            # TODO Track components added here
            entry = getRandomEntry('H') + entry + getRandomEntry('K')
            descriptors.append(entry)
            componentsAdded += 1
        else:
            if entry:
                descriptors.append(entry)
                componentsAdded += 1
            break
    components = descriptors + components

    # Curse
    entry = getRandomEntry('G')
    if entry:
        components.insert(0, entry)
        componentsAdded += 1

    # Quantity
    entry = getRandomEntry('F')
    if entry and subjectPlurality != Plurality.SINGULAR:
        components.insert(0, entry)
        componentsAdded += 1

    # Pre Everything
    if subjectPlurality == Plurality.SINGULAR:
        entry = getRandomEntry('D', 'E')
        componentsAdded += 1
    else:
        entry = getRandomEntry('D')
        componentsAdded += 1
    if entry:
        components.insert(0, entry)
        componentsAdded += 1

    # Post Subject
    if subjectPlurality != Plurality.PLURAL:
        coords = getRandomCoords('P', 'Q')
        entry = getEntry(coords)
        if entry:
            newCoords = [coords[0], coords[1] + 1]
            if subjectEndsInVowel and getEntry(newCoords):
                entry = getEntry(newCoords)
            components[-1] = components[-1] + entry
            componentsAdded += 1

    # Modifier
    entry = getRandomEntry('T')
    if entry:
        components.append(entry)
        componentsAdded += 1

    # Post Everything
    entry = getRandomEntry('U')
    if entry:
        components.append(entry)
        componentsAdded += 1

    # TODO Replace all double spaces with single spaces
    # TODO Make sure the same word can't appear more than once
    # TODO Multiple subjects
    # TODO Fix bias with selecting individual items from different columns
    #      (calculate a ratio of filled-to-unfilled cells for each column)
    # TODO Make the | separator work

    # Abort if nothing new was added
    # TODO: Make this a low chance instead of automatic?
    if componentsAdded <= 1:
        return ""

    result = ' '.join(components)

    # Replace 'a' with 'an'
    result = result.split(' ')
    i = 0
    while i < len(result) - 1:
        if result[i] == 'a' and isVowel(result[i + 1][0]):
            result[i] = 'an'
        i += 1
    result = ' '.join(result)

    # Capitalization
    result = titlecase(result)

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
    if nickname:
        print(nickname)
        i += 1
