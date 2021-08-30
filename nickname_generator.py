import random
import sheet_info
from vowel_checker import is_vowel
from titlecase import titlecase


_data = []
_column_weights = []
_num_rows = 0
_num_cols = 0


class Plurality:
    ANY = 0
    SINGULAR = 1
    PLURAL = 2


def _get_random_coords_from_tuple(cols):
    rand_row = random.randrange(sheet_info.ROW_OFFSET, _num_rows)
    weights = []
    for col in cols:
        weights.append(_column_weights[col])
    rand_col = random.choices(cols, weights)[0]
    return [rand_row, rand_col]


def _get_random_coords(*cols):
    return _get_random_coords_from_tuple(cols)


def _get_random_entry(*cols):
    coords = _get_random_coords_from_tuple(cols)
    return _get_entry(coords)


def _get_entry(coords):
    entry = _data[coords[0]][coords[1]]
    if '|' in entry:
        entries = entry.split('|')
        return random.choice(entries)
    else:
        return entry


def generate_nickname():
    entry = ""
    components = []
    components_added = 0
    subject_plurality = -1
    subject_ends_in_vowel = False

    # Any subject, don't proceed until one is found
    while not components:
        coords = _get_random_coords_from_tuple(sheet_info.ALL_SUBJECTS)
        entry = _get_entry(coords)
        if entry:
            components.append(entry)
            if coords[1] == sheet_info.SUBJECT_ANY:
                subject_plurality = Plurality.ANY
            elif coords[1] == sheet_info.SUBJECT_SINGULAR:
                subject_plurality = Plurality.SINGULAR
            elif coords[1] == sheet_info.SUBJECT_PLURAL:
                subject_plurality = Plurality.PLURAL
            subject_ends_in_vowel = is_vowel(entry[-1])

    # Pre Subject
    entry = _get_random_entry(sheet_info.PRE_SUBJECT)
    if entry:
        components[0] = entry + components[0]
        components_added += 1

    # Adjectives/Descriptors
    descriptors = []
    while True:
        coords = _get_random_coords(sheet_info.ADJECTIVE, sheet_info.DESCRIPTOR)
        entry = _get_entry(coords)
        if entry and coords[1] == sheet_info.ADJECTIVE:
            entry2 = _get_random_entry(sheet_info.ADVERB)
            if entry2:
                descriptors.append(entry2)
                components_added += 1

            entry2 = _get_random_entry(sheet_info.POST_ADJECTIVE)
            if entry2:
                entry = entry + entry2
                components_added += 1

            descriptors.append(entry)

            components_added += 1
        else:
            if entry:
                descriptors.append(entry)
                components_added += 1
            break
    components = descriptors + components

    # Curse
    entry = _get_random_entry(sheet_info.CURSE)
    if entry:
        components.insert(0, entry)
        components_added += 1

    # Quantity
    entry = _get_random_entry(sheet_info.QUANTITY_PLURAL)
    if entry and subject_plurality != Plurality.SINGULAR:
        components.insert(0, entry)
        components_added += 1

    # Pre Everything
    if subject_plurality == Plurality.SINGULAR:
        entry = _get_random_entry(sheet_info.PRE_EVERYTHING, sheet_info.PRE_EVERYTHING_SINGULAR)
        components_added += 1
    else:
        entry = _get_random_entry(sheet_info.PRE_EVERYTHING)
        components_added += 1
    if entry:
        components.insert(0, entry)
        components_added += 1

    # Post Subject
    if subject_plurality != Plurality.PLURAL:
        coords = _get_random_coords(sheet_info.POST_SUBJECT_SINGULAR)
        entry = _get_entry(coords)
        if entry:
            new_coords = [coords[0], sheet_info.POST_SUBJECT_AFTER_VOWEL]
            if subject_ends_in_vowel and _get_entry(new_coords):
                entry = _get_entry(new_coords)
            components[-1] = components[-1] + entry
            components_added += 1

    # Modifier
    entry = _get_random_entry(sheet_info.MODIFIER)
    if entry:
        components.append(entry)
        components_added += 1

    # Post Everything
    entry = _get_random_entry(sheet_info.POST_EVERYTHING)
    if entry:
        components.append(entry)
        components_added += 1

    # TODO Replace all double spaces with single spaces
    # TODO Make sure the same word can't appear more than once
    # TODO Multiple subjects
    # TODO Replace the first syllable (as with "ya'llternative")
    # TODO Think harder about certain multi subject separators (like "up in the")

    # Abort if nothing new was added
    # TODO: Make this a low chance instead of automatic?
    if components_added <= 1:
        return ""

    result = ' '.join(components)

    # Replace 'a' with 'an'
    result = result.split(' ')
    i = 0
    while i < len(result) - 1:
        if result[i] == 'a' and is_vowel(result[i + 1][0]):
            result[i] = 'an'
        i += 1
    result = ' '.join(result)

    # Capitalization
    result = titlecase(result)

    return result


def _generate_column_weights():
    global _column_weights
    _column_weights = []
    i = 0
    while i < _num_cols:
        count = 0
        j = 0
        while j < _num_rows:
            entry = _data[j][i]
            if entry:
                count += 1 + entry.count('|')
            j += 1
        _column_weights.append(count)
        i += 1


def set_data(new_data):
    global _data
    _data = new_data
    global _num_rows
    _num_rows = len(_data)
    global _num_cols
    _num_cols = len(_data[0])
    print("Nickname data set with %s rows x %s cols" % (_num_rows, _num_cols))

    _generate_column_weights()