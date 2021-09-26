class Incrementer:

    def increment(self):
        self.value += 1
        return self.value

    def __init__(self, start):
        self.value = start - 1