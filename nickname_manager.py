import random
from nickname_generator import generate_nickname


nicks = {}


class Nickname:
    base_seed = random.randrange(9999999)
    index = 0
    show_source = False
    generator = random.Random()

    def seed(self):
        return self.base_seed + self.index

    def generate(self):
        self.generator.seed(self.seed())
        result = ""
        while result == "":
            result = generate_nickname(self.generator)
        return result


def remember(message_id, nickname):
    nicks[message_id] = nickname


def get_next(message_id):
    nick = nicks[message_id]
    nick.index += 1
    return nick.generate()


def get_prev(message_id):
    nick = nicks[message_id]
    if nick.index > 0:
        nick.index -= 1
    return nick.generate()
