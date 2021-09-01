from titlecase import titlecase

import sheet_info
from vowel_checker import is_vowel

_data = []
_column_weights = []
_num_rows = 0
_num_cols = 0
_LOG_HIGHLIGHT = "__"


class Plurality:
    ANY = 0
    SINGULAR = 1
    PLURAL = 2


def _get_random_coords_from_tuple(generator, cols):
    rand_row = generator.randrange(sheet_info.ROW_OFFSET, _num_rows)
    weights = []
    for col in cols:
        weights.append(_column_weights[col])
    rand_col = generator.choices(cols, weights)[0]
    return [rand_row, rand_col]


def _get_random_coords(generator, *cols):
    return _get_random_coords_from_tuple(generator, cols)


def _get_random_entry(generator, *cols):
    coords = _get_random_coords_from_tuple(generator, cols)
    return _get_entry(generator, coords)


def _get_entry(generator, coords):
    entry = _data[coords[0]][coords[1]]
    if '|' in entry:
        entries = entry.split('|')
        entry = generator.choice(entries)

    source = _data[coords[0]][sheet_info.NICKNAME]
    if entry:
        try:
            start_index = source.lower().index(entry.lower())
            end_index = start_index + len(entry)
            source = source[:start_index] + _LOG_HIGHLIGHT + source[start_index:end_index] + _LOG_HIGHLIGHT + source[end_index:]
        except ValueError:
            print("%s not found in %s" % (entry, source))

    return entry, source


def generate_nickname(generator):
    entry = ""
    components = []
    log = []
    subject_plurality = -1
    subject_ends_in_vowel = False

    # Any subject, don't proceed until one is found
    while not components:
        coords = _get_random_coords_from_tuple(generator, sheet_info.ALL_SUBJECTS)
        entry, source = _get_entry(generator, coords)
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
    entry, source = _get_random_entry(generator, sheet_info.PRE_SUBJECT)
    if entry:
        components[0] = entry + components[0]
        log.insert(0, source)

    # Adjectives/Descriptors
    descriptors = []
    log_descriptors = []
    while True:
        coords = _get_random_coords(generator, sheet_info.ADJECTIVE, sheet_info.DESCRIPTOR)
        entry, source = _get_entry(generator, coords)
        if entry and coords[1] == sheet_info.ADJECTIVE:
            entry2, source2 = _get_random_entry(generator, sheet_info.ADVERB)
            if entry2:
                descriptors.append(entry2)
                log_descriptors.append(source2)

            log_descriptors.append(source)

            entry2, source2 = _get_random_entry(generator, sheet_info.POST_ADJECTIVE)
            if entry2:
                entry = entry + entry2
                log_descriptors.append(source2)

            descriptors.append(entry)
        else:
            if entry:
                descriptors.append(entry)
                log_descriptors.append(source)
            break
    components = descriptors + components
    log = log_descriptors + log

    # Curse
    entry, source = _get_random_entry(generator, sheet_info.CURSE)
    if entry:
        components.insert(0, entry)
        log.insert(0, source)

    # Quantity
    entry, source = _get_random_entry(generator, sheet_info.QUANTITY_PLURAL)
    if entry and subject_plurality != Plurality.SINGULAR:
        components.insert(0, entry)
        log.insert(0, source)

    # Pre Everything
    if subject_plurality == Plurality.SINGULAR:
        entry, source = _get_random_entry(generator, sheet_info.PRE_EVERYTHING, sheet_info.PRE_EVERYTHING_SINGULAR)
    else:
        entry, source = _get_random_entry(generator, sheet_info.PRE_EVERYTHING)
    if entry:
        components.insert(0, entry)
        log.insert(0, source)

    # Post Subject
    if subject_plurality != Plurality.PLURAL:
        coords = _get_random_coords(generator, sheet_info.POST_SUBJECT_SINGULAR)
        entry, source = _get_entry(generator, coords)
        if entry:
            new_coords = [coords[0], sheet_info.POST_SUBJECT_AFTER_VOWEL]
            if subject_ends_in_vowel and _get_entry(generator, new_coords)[0]:
                entry, source = _get_entry(generator, new_coords)
            components[-1] = components[-1] + entry
            log.append(source)

    # Modifier
    if subject_plurality != Plurality.PLURAL:
        entry, source = _get_random_entry(generator, sheet_info.MODIFIER)
        if entry:
            components.append(entry)
            log.append(source)

    # Post Everything
    entry, source = _get_random_entry(generator, sheet_info.POST_EVERYTHING)
    if entry:
        components.append(entry)
        log.append(source)

    # TODO Multiple subjects
    # TODO Replace the first syllable (as with "ya'llternative")
    # TODO Think harder about certain multi subject separators (like "up in the")
    # TODO Change "spreading" to allow for things like "Spreading Kuzco's Poison"

    # Abort if nothing new was added
    # TODO Make this a low chance instead of automatic?
    if len(log) <= 1:
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

    return result, log_result


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
