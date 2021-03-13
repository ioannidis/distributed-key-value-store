import collections
import random
from faker import Faker


class DataGenerator:

    def __init__(self, options, keys):
        self.options = options
        self.keys = keys
        self.data = []

        self.fake = Faker()

    def get_data(self):
        return self.data

    def generate(self):
        for i in range(int(self.options['n']) - 89):
            self.depth = random.randint(0, int(self.options['d']))
            self.maxKeys = random.randint(0, int(self.options['m']))

            self.d = {f'person{i}': {}}
            self.dict_helper(self.d, f'person{i}')
            self.data.append(self.d)

    def dict_helper(self, lvl, key):

        # print(self.d)
        if not self.depth:
            return

        self.depth -= 1

        selected_keys = set()
        for _ in range(2):

            while True:
                random_key = random.choice(self.keys)
                if random_key[0] not in selected_keys:
                    break
            selected_keys.add(random_key[0])

            if random.random() > 0.5:
                lvl[key][random_key[0]] = self.get_fake_value(random_key[1])
            else:
                if self.depth == 0:
                    lvl[key][random_key[0]] = self.get_fake_value(random_key[1])
                else:
                    lvl[key][random_key[0]] = {}
                    self.dict_helper(lvl[key], random_key[0])


    def get_fake_value(self, type):
        if type == 'string':
            placeholder = '?' * random.randint(1, int(self.options['l']))
            return self.fake.bothify(text=placeholder)
        elif type == 'int':
            return random.randint(0, 1000)
        elif type == 'float':
            return random.uniform(0, 100)
        else:
            return True if random.random() > 0.5 else False
