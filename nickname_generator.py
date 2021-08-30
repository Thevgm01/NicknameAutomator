import random
from titlecase import titlecase

import sheet_info
from vowel_checker import is_vowel

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
        entry = random.choice(entries)

    source = _data[coords[0]][sheet_info.NICKNAME]
    if entry:
        try:
            start_index = source.lower().index(entry.lower())
            end_index = start_index + len(entry)
            source = source[:start_index] + "**" + source[start_index:end_index] + "**" + source[end_index:]
        except ValueError:
            print("%s not found in %s" % (entry, source))

    return entry, source


def _generate_nickname():
    entry = ""
    components = []
    log = []
    components_added = 0
    subject_plurality = -1
    subject_ends_in_vowel = False

    # Any subject, don't proceed until one is found
    while not components:
        coords = _get_random_coords_from_tuple(sheet_info.ALL_SUBJECTS)
        entry, source = _get_entry(coords)
        if entry:
            components.append(entry)
            log.append(source)
            if coords[1] == sheet_info.SUBJECT_ANY:
                subject_plurality = Plurality.ANY
            elif coords[1] == sheet_info.SUBJECT_SINGULAR:
                subject_plurality = Plurality.SINGULAR
            elif coords[1] == sheet_info.SUBJECT_PLURAL:
                subject_plurality = Plurality.PLURAL
            subject_ends_in_vowel = is_vowel(entry[-1])

    # Pre Subject
    entry, source = _get_random_entry(sheet_info.PRE_SUBJECT)
    if entry:
        components[0] = entry + components[0]
        log.append(source)
        components_added += 1

    # Adjectives/Descriptors
    descriptors = []
    while True:
        coords = _get_random_coords(sheet_info.ADJECTIVE, sheet_info.DESCRIPTOR)
        entry, source = _get_entry(coords)
        if entry and coords[1] == sheet_info.ADJECTIVE:
            entry2, source2 = _get_random_entry(sheet_info.ADVERB)
            if entry2:
                descriptors.append(entry2)
                log.append(source2)
                components_added += 1

            entry2, source2 = _get_random_entry(sheet_info.POST_ADJECTIVE)
            if entry2:
                entry = entry + entry2
                log.append(source2)
                components_added += 1

            descriptors.append(entry)
            log.append(source)
            components_added += 1
        else:
            if entry:
                descriptors.append(entry)
                log.append(source)
                components_added += 1
            break
    components = descriptors + components

    # Curse
    entry, source = _get_random_entry(sheet_info.CURSE)
    if entry:
        components.insert(0, entry)
        log.append(source)
        components_added += 1

    # Quantity
    entry, source = _get_random_entry(sheet_info.QUANTITY_PLURAL)
    if entry and subject_plurality != Plurality.SINGULAR:
        components.insert(0, entry)
        log.append(source)
        components_added += 1

    # Pre Everything
    if subject_plurality == Plurality.SINGULAR:
        entry, source = _get_random_entry(sheet_info.PRE_EVERYTHING, sheet_info.PRE_EVERYTHING_SINGULAR)
    else:
        entry, source = _get_random_entry(sheet_info.PRE_EVERYTHING)
    if entry:
        components.insert(0, entry)
        log.append(source)
        components_added += 1

    # Post Subject
    if subject_plurality != Plurality.PLURAL:
        coords = _get_random_coords(sheet_info.POST_SUBJECT_SINGULAR)
        entry, source = _get_entry(coords)
        if entry:
            new_coords = [coords[0], sheet_info.POST_SUBJECT_AFTER_VOWEL]
            if subject_ends_in_vowel and _get_entry(new_coords):
                entry, source = _get_entry(new_coords)
            components[-1] = components[-1] + entry
            log.append(source)
            components_added += 1

    # Modifier
    if subject_plurality != Plurality.PLURAL:
        entry, source = _get_random_entry(sheet_info.MODIFIER)
        if entry:
            components.append(entry)
            log.append(source)
            components_added += 1

    # Post Everything
    entry, source = _get_random_entry(sheet_info.POST_EVERYTHING)
    if entry:
        components.append(entry)
        log.append(source)
        components_added += 1

    # TODO Replace all double spaces with single spaces
    # TODO Make sure the same word can't appear more than once
    # TODO Multiple subjects
    # TODO Replace the first syllable (as with "ya'llternative")
    # TODO Think harder about certain multi subject separators (like "up in the")
    # TODO Change "spreading" to allow for things like "Spreading Kuzco's Poison"
    # TODO Fix logging, extras are still being added to the end as with:
    #       Blursed_pasta
    #       Forest **Pasta**
    #       Baja **blursed_**images
    #       The Corkinator

    # Abort if nothing new was added
    # TODO Make this a low chance instead of automatic?
    if components_added <= 1:
        return ""

    # Ensure the same word can't appear twice
    i = 0
    while i < len(components) - 1:
        if components[i] not in ["a", "an", "ol'", "the"]:
            j = i + 1
            while j < len(components):
                if components[i] == components[j]:
                    return ""
                j += 1
        i += 1

    result = ' '.join(components)
    result = result.split(' ')

    # Replace 'a' with 'an'
    i = 0
    while i < len(result) - 1:
        if result[i] == 'a' and is_vowel(result[i + 1][0]):
            result[i] = 'an'
        i += 1
    result = ' '.join(result)

    # Capitalization
    result = titlecase(result)

    log_result = '\n'.join(log)
    print(result)
    print(log_result)
    print("-----------------")

    return result


def generate_nickname():
    result = ""
    while result == "":
        result = _generate_nickname()
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
