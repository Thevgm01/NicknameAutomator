import random
from nickname_generator import generate_nickname


nicks = {}


class Nickname:
    index = 0
    show_source = False

    def seed(self):
        return self.base_seed + self.index

    def toggle_source(self):
        self.show_source = not self.show_source
        return self.generate()

    def generate(self):
        self.generator.seed(self.seed())
        result = ""
        while result == "":
            result = generate_nickname(self.generator)

        if self.show_source:
            return '\n'.join(result)
        else:
            return result[0]

    def __init__(self, seed=0):
        self.generator = random.Random()
        if seed:
            self.base_seed = seed
        else:
            self.base_seed = self.generator.randrange(999999999)


def remember(message_id, nickname):
    nicks[message_id] = nickname


def toggle_source(message_id):
    return nicks[message_id].toggle_source()


def get_next(message_id):
    nick = nicks[message_id]
    nick.index += 1
    return nick.generate()


def get_prev(message_id):
    nick = nicks[message_id]
    nick.index -= 1
    return nick.generate()
