VOWELS = ['a', 'e', 'i', 'o', 'u', 'y']


def is_vowel(letter):
    letter = letter.lower()
    for v in VOWELS:
        if v == letter:
            return True
    return False


def is_consonant(letter):
    return not is_vowel(letter)
