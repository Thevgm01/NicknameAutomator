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


ROW_OFFSET = 1
COL_OFFSET = 3


class WordType:
    PRE_EVERYTHING = mapLetter('D')
    PRE_EVERYTHING_SINGULAR = mapLetter('E')
    QUANTITY_PLURAL = mapLetter('F')
    CURSE = mapLetter('G')
    ADVERB = mapLetter('H')
    ADJECTIVE = mapLetter('I')
    POST_ADJECTIVE = mapLetter('J')
    DESCRIPTOR = mapLetter('K')
    PRE_SUBJECT = mapLetter('L')
    SUBJECT_ANY = mapLetter('M')
    SUBJECT_SINGULAR = mapLetter('N')
    SUBJECT_PLURAL = mapLetter('O')
    POST_SUBJECT_SINGULAR = mapLetter('P')
    POST_SUBJECT_AFTER_VOWEL = mapLetter('Q')
    MULTI_OBJECT_SEPARATOR = mapLetter('R')
    MODIFIER = mapLetter('S')
    POST_EVERYTHING = mapLetter('T')

    ALL_SUBJECTS = (SUBJECT_ANY, SUBJECT_SINGULAR, SUBJECT_PLURAL)


def getRandomCoordsFromTuple(cols):
    randRow = random.randrange(ROW_OFFSET, numRows)
    weights = []
    for col in cols:
        weights.append(columnWeights[col])
    randCol = random.choices(cols, weights)[0]
    #randCol = random.choice(cols)
    return [randRow, randCol]


def getRandomCoords(*cols):
    return getRandomCoordsFromTuple(cols)


def getRandomEntry(*cols):
    coords = getRandomCoordsFromTuple(cols)
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
        coords = getRandomCoordsFromTuple(WordType.ALL_SUBJECTS)
        entry = getEntry(coords)
        if entry:
            components.append(entry)
            if coords[1] == WordType.SUBJECT_ANY:
                subjectPlurality = Plurality.ANY
            elif coords[1] == WordType.SUBJECT_SINGULAR:
                subjectPlurality = Plurality.SINGULAR
            elif coords[1] == WordType.SUBJECT_PLURAL:
                subjectPlurality = Plurality.PLURAL
            subjectEndsInVowel = isVowel(entry[-1])

    # Pre Subject
    entry = getRandomEntry(WordType.PRE_SUBJECT)
    if entry:
        components[0] = entry + components[0]
        componentsAdded += 1

    # Adjectives/Descriptors
    descriptors = []
    while True:
        coords = getRandomCoords(WordType.ADJECTIVE, WordType.DESCRIPTOR)
        entry = getEntry(coords)
        if entry and coords[1] == WordType.ADJECTIVE:
            entry2 = getRandomEntry(WordType.ADVERB)
            if entry2:
                hasAdverb = True
                descriptors.append(entry2)
                componentsAdded += 1

            entry2 = getRandomEntry(WordType.POST_ADJECTIVE)
            if entry2:
                entry = entry + entry2
                componentsAdded += 1

            descriptors.append(entry)

            componentsAdded += 1
        else:
            if entry:
                descriptors.append(entry)
                componentsAdded += 1
            break
    components = descriptors + components

    # Curse
    entry = getRandomEntry(WordType.CURSE)
    if entry:
        components.insert(0, entry)
        componentsAdded += 1

    # Quantity
    entry = getRandomEntry(WordType.QUANTITY_PLURAL)
    if entry and subjectPlurality != Plurality.SINGULAR:
        components.insert(0, entry)
        componentsAdded += 1

    # Pre Everything
    if subjectPlurality == Plurality.SINGULAR:
        entry = getRandomEntry(WordType.PRE_EVERYTHING, WordType.PRE_EVERYTHING_SINGULAR)
        componentsAdded += 1
    else:
        entry = getRandomEntry(WordType.PRE_EVERYTHING)
        componentsAdded += 1
    if entry:
        components.insert(0, entry)
        componentsAdded += 1

    # Post Subject
    if subjectPlurality != Plurality.PLURAL:
        coords = getRandomCoords(WordType.POST_SUBJECT_SINGULAR)
        entry = getEntry(coords)
        if entry:
            newCoords = [coords[0], WordType.POST_SUBJECT_AFTER_VOWEL]
            if subjectEndsInVowel and getEntry(newCoords):
                entry = getEntry(newCoords)
            components[-1] = components[-1] + entry
            componentsAdded += 1

    # Modifier
    entry = getRandomEntry(WordType.MODIFIER)
    if entry:
        components.append(entry)
        componentsAdded += 1

    # Post Everything
    entry = getRandomEntry(WordType.POST_EVERYTHING)
    if entry:
        components.append(entry)
        componentsAdded += 1

    # TODO Replace all double spaces with single spaces
    # TODO Make sure the same word can't appear more than once
    # TODO Multiple subjects

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


def generateColumnWeights():
    weights = []
    i = 0
    while i < numCols:
        count = 0
        j = 0
        while j < numRows:
            entry = data[j][i]
            if entry:
                count += 1 + entry.count('|')
            j += 1
        weights.append(count)
        i += 1
    return weights


scope = ["https://spreadsheets.google.com/feeds",
         "https://www.googleapis.com/auth/spreadsheets",
         "https://www.googleapis.com/auth/drive.file",
         "https://www.googleapis.com/auth/drive"]

credentials = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(credentials)
sheet = client.open("Nickname Categorization").sheet1  # Open the spreadsheet
data = sheet.get_all_values()  # Get a list of all records

numRows = len(data)
numCols = len(data[0])
print("%s rows x %s cols" % (numRows, numCols))
columnWeights = generateColumnWeights()

num = 0
while num < 50:
    nickname = generateNickname()
    if nickname:
        print(nickname)
        num += 1
