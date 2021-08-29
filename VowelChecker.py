VOWELS = ['a', 'e', 'i', 'o', 'u', 'y']


def isVowel(letter):
    letter = letter.lower()
    for v in VOWELS:
        if v == letter:
            return True
    return False


def isConsonant(letter):
    return not isVowel(letter)
