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
        for i in range(int(self.options['n'])):
            self.depth = random.randint(0, int(self.options['d']))
            self.maxKeys = random.randint(0, int(self.options['m']))

            self.d = f'"person{i}":' + str(self.dict_helper())
            self.data.append(self.d)

    def dict_helper(self):

        # print(self.d)
        if not self.depth:
            return ' { } '

        self.depth -= 1

        selected_keys = set()
        s = ' { '
        for i in range(self.maxKeys):

            while True:
                random_key = random.choice(self.keys)
                if random_key[0] not in selected_keys:
                    break
            selected_keys.add(random_key[0])

            key = f'"{random_key[0]}"'
            if self.depth == 0:
                s = s + key + ' : ' + str(self.get_fake_value(random_key[1]))
            else:
                if random.random() > 0.65:
                    s = s + key + ' : ' + str(self.get_fake_value(random_key[1]))
                else:
                    s = s + key + ' : ' + self.dict_helper()

            if i < self.maxKeys-1:
                s += ' ; '

        s += ' } '
        return s


    def get_fake_value(self, type):
        if type == 'string':
            placeholder = '?' * random.randint(1, int(self.options['l']))
            return f'"{self.fake.bothify(text=placeholder)}"'
        elif type == 'int':
            return random.randint(0, 1000)
        elif type == 'float':
            return round(random.uniform(0, 100), 3)
        else:
            return True if random.random() > 0.5 else False
