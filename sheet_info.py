from incrementer import Incrementer


def _map_letter(letter):
    return ord(letter.upper()) - ord('A')


SHEET_NAME = "Nickname Categorization"

ROW_OFFSET = 1
COL_OFFSET = 3

i = Incrementer(_map_letter('C'))
NICKNAME = i.increment()
PRE_EVERYTHING = i.increment()
PRE_EVERYTHING_SINGULAR = i.increment()
QUANTITY_PLURAL = i.increment()
CURSE = i.increment()
ADVERB = i.increment()
ADJECTIVE = i.increment()
POST_ADJECTIVE = i.increment()
DESCRIPTOR = i.increment()
PRE_SUBJECT = i.increment()
SUBJECT_ANY = i.increment()
SUBJECT_SINGULAR = i.increment()
SUBJECT_PLURAL = i.increment()
POST_SUBJECT_SINGULAR = i.increment()
POST_SUBJECT_AFTER_VOWEL = i.increment()
MULTI_SUBJECT_SEPARATOR = i.increment()
MODIFIER = i.increment()
POST_EVERYTHING = i.increment()

ALL_SUBJECTS = (SUBJECT_ANY, SUBJECT_SINGULAR, SUBJECT_PLURAL)
ADDITIONAL_SUBJECT_COMPONENTS = (CURSE, ADVERB, ADJECTIVE, POST_ADJECTIVE, DESCRIPTOR, ALL_SUBJECTS)

NICKNAME_MESSAGE_ID_COL = 1
NICKNAME_MESSAGE_SEED_COL = 2