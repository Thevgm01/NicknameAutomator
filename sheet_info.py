def _map_letter(letter):
    return ord(letter.upper()) - ord('A')


SHEET_NAME = "Nickname Categorization"

ROW_OFFSET = 1
COL_OFFSET = 3

PRE_EVERYTHING = _map_letter('D')
PRE_EVERYTHING_SINGULAR = _map_letter('E')
QUANTITY_PLURAL = _map_letter('F')
CURSE = _map_letter('G')
ADVERB = _map_letter('H')
ADJECTIVE = _map_letter('I')
POST_ADJECTIVE = _map_letter('J')
DESCRIPTOR = _map_letter('K')
PRE_SUBJECT = _map_letter('L')
SUBJECT_ANY = _map_letter('M')
SUBJECT_SINGULAR = _map_letter('N')
SUBJECT_PLURAL = _map_letter('O')
POST_SUBJECT_SINGULAR = _map_letter('P')
POST_SUBJECT_AFTER_VOWEL = _map_letter('Q')
MULTI_SUBJECT_SEPARATOR = _map_letter('R')
MODIFIER = _map_letter('S')
POST_EVERYTHING = _map_letter('T')

ALL_SUBJECTS = (SUBJECT_ANY, SUBJECT_SINGULAR, SUBJECT_PLURAL)
ADDITIONAL_SUBJECT_COMPONENTS = (CURSE, ADVERB, ADJECTIVE, POST_ADJECTIVE, DESCRIPTOR, ALL_SUBJECTS)
