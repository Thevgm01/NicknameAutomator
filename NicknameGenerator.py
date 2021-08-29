import random
import SheetInfo
from VowelChecker import isVowel
from titlecase import titlecase


data = None
columnWeights = None
numRows = None
numCols = None


class Plurality:
    ANY = 0
    SINGULAR = 1
    PLURAL = 2


def getRandomCoordsFromTuple(cols):
    randRow = random.randrange(SheetInfo.ROW_OFFSET, numRows)
    weights = []
    for col in cols:
        weights.append(columnWeights[col])
    randCol = random.choices(cols, weights)[0]
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
        coords = getRandomCoordsFromTuple(SheetInfo.ALL_SUBJECTS)
        entry = getEntry(coords)
        if entry:
            components.append(entry)
            if coords[1] == SheetInfo.SUBJECT_ANY:
                subjectPlurality = Plurality.ANY
            elif coords[1] == SheetInfo.SUBJECT_SINGULAR:
                subjectPlurality = Plurality.SINGULAR
            elif coords[1] == SheetInfo.SUBJECT_PLURAL:
                subjectPlurality = Plurality.PLURAL
            subjectEndsInVowel = isVowel(entry[-1])

    # Pre Subject
    entry = getRandomEntry(SheetInfo.PRE_SUBJECT)
    if entry:
        components[0] = entry + components[0]
        componentsAdded += 1

    # Adjectives/Descriptors
    descriptors = []
    while True:
        coords = getRandomCoords(SheetInfo.ADJECTIVE, SheetInfo.DESCRIPTOR)
        entry = getEntry(coords)
        if entry and coords[1] == SheetInfo.ADJECTIVE:
            entry2 = getRandomEntry(SheetInfo.ADVERB)
            if entry2:
                hasAdverb = True
                descriptors.append(entry2)
                componentsAdded += 1

            entry2 = getRandomEntry(SheetInfo.POST_ADJECTIVE)
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
    entry = getRandomEntry(SheetInfo.CURSE)
    if entry:
        components.insert(0, entry)
        componentsAdded += 1

    # Quantity
    entry = getRandomEntry(SheetInfo.QUANTITY_PLURAL)
    if entry and subjectPlurality != Plurality.SINGULAR:
        components.insert(0, entry)
        componentsAdded += 1

    # Pre Everything
    if subjectPlurality == Plurality.SINGULAR:
        entry = getRandomEntry(SheetInfo.PRE_EVERYTHING, SheetInfo.PRE_EVERYTHING_SINGULAR)
        componentsAdded += 1
    else:
        entry = getRandomEntry(SheetInfo.PRE_EVERYTHING)
        componentsAdded += 1
    if entry:
        components.insert(0, entry)
        componentsAdded += 1

    # Post Subject
    if subjectPlurality != Plurality.PLURAL:
        coords = getRandomCoords(SheetInfo.POST_SUBJECT_SINGULAR)
        entry = getEntry(coords)
        if entry:
            newCoords = [coords[0], SheetInfo.POST_SUBJECT_AFTER_VOWEL]
            if subjectEndsInVowel and getEntry(newCoords):
                entry = getEntry(newCoords)
            components[-1] = components[-1] + entry
            componentsAdded += 1

    # Modifier
    entry = getRandomEntry(SheetInfo.MODIFIER)
    if entry:
        components.append(entry)
        componentsAdded += 1

    # Post Everything
    entry = getRandomEntry(SheetInfo.POST_EVERYTHING)
    if entry:
        components.append(entry)
        componentsAdded += 1

    # TODO Replace all double spaces with single spaces
    # TODO Make sure the same word can't appear more than once
    # TODO Multiple subjects
    # TODO Replace the first syllable (as with "ya'llternative")
    # TODO Think harder about certain multi subject separators (like "up in the")

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
    global columnWeights
    columnWeights = []
    i = 0
    while i < numCols:
        count = 0
        j = 0
        while j < numRows:
            entry = data[j][i]
            if entry:
                count += 1 + entry.count('|')
            j += 1
        columnWeights.append(count)
        i += 1


def setData(newData):
    global data
    data = newData
    global numRows
    numRows = len(data)
    global numCols
    numCols = len(data[0])
    print("Nickname data set with %s rows x %s cols" % (numRows, numCols))

    generateColumnWeights()
