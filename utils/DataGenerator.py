import random
from faker import Faker


class DataGenerator:

    def __init__(self, options, keys):
        self._options = options
        self._keys = keys
        self._data = []

        self._fake = Faker()

    def get_data(self):
        return self._data

    def generate(self):
        for i in range(self._options.n):
            depth = random.randint(0, self._options.d)

            d = f'"person{i}":' + str(self.dict_helper(depth))
            self._data.append(d)

    def dict_helper(self, depth):

        if depth == -1:
            return '{}'

        depth -= 1

        max_keys = random.randint(0, self._options.m)

        selected_keys = set()
        s = ' { '
        for i in range(max_keys):

            while True:
                random_key = random.choice(self._keys)
                if random_key[0] not in selected_keys:
                    break
            selected_keys.add(random_key[0])

            key, key_type = f'"{random_key[0]}"', random_key[1]
            if depth == -1:
                s = s + key + ' : ' + str(self.get_fake_value(key_type))
            else:
                if random.random() > 0.4:
                    s = s + key + ' : ' + str(self.get_fake_value(key_type))
                else:
                    s = s + key + ' : ' + self.dict_helper(depth)

            if i < max_keys-1:
                s += ' ; '

        s += ' } '
        return s


    def get_fake_value(self, type):
        if type == 'string':
            placeholder = '?' * random.randint(1, int(self._options.l))
            return f'"{self._fake.bothify(text=placeholder)}"'
        elif type == 'int':
            return random.randint(0, 1000)
        elif type == 'float':
            return round(random.uniform(0, 100), 3)
        else:
            return True if random.random() > 0.5 else False
