import collections
import json
import tokenize


class TrieNode:

    def __init__(self, char, value=None, is_key=False) -> None:
        self.children = collections.defaultdict(TrieNode)
        self.char = char
        self.value = value
        self.is_key = is_key
        self.occurrences = 1

    def insert(self, key, levels={}):
        if not key:
            self.is_key = True
            if levels:
                if not self.value:
                    self.value = TrieNode('*')

                if isinstance(levels, dict):
                    for k, v in levels.items():
                        self.value.insert(k, v)
                else:
                    self.value = levels
            return

        c = key[0]
        if c in self.children:
            node = self.children[c]
            node.occurrences += 1
            node.insert(key[1:], levels)
        else:
            self.children[c] = TrieNode(c)
            self.children[c].insert(key[1:], levels)

    def remove(self, key):
        if not key:
            if self.is_key:
                self.value = None
                self.is_key = False
                return True
            return False

        c = key[0]
        if c in self.children:
            node = self.children[c]
            is_deleted = node.remove(key[1:])

            if is_deleted:
                node.occurrences -= 1
                if not node.occurrences:
                    del self.children[c]

            return is_deleted

        return False

    def search(self, key, levels=[]):

        if not key:
            if not self.is_key:
                return

            if not levels:
                if self.is_key:
                    if self.value:
                        return self.value
                    else:
                        return '{}'
                return
            else:
                return self.value.search(levels[0], levels[1:])

        if key[0] not in self.children:
            return

        return self.children[key[0]].search(key[1:], levels)

    def find_path(self, s):
        s = s.split('.')
        return self.search(s[0], s[1:])

    def find(self, s):
        return self.search(s)

    # Res builder pre-order
    def res_builder(self, node, s, branch, depth):

        if node.is_key:
            if isinstance(node.value, TrieNode):
                temp_s = s
                branch[temp_s] = {}
                self.res_builder(node.value, '', branch[temp_s], depth + 1)
            else:
                branch[s] = node.value

        else:
            for k, c in node.children.items():
                self.res_builder(c, s + k, branch, depth)


def test(node):
    res = None
    if not node:
        return

    if not isinstance(node, TrieNode):
        res = node
    else:
        res = {}
        node.res_builder(node, '', res, 0)
        # if node.char == '*':
        # for k, c in node.children.items():
        #     b = {}
        #     root.res_builder(c, k, b, 0)

    return res

def load_data():
    f = open('dataToIndex.txt', 'r')
    data, line = [], []
    for token in tokenize.generate_tokens(f.readline):
        if token[0] == tokenize.NEWLINE:
            data.append("".join(line))
            line = []
        elif token[0] == tokenize.OP and token[1] == ';':
            line.append(',')
        else:
            line.append(token[1])
    f.close()
    return data

# if __name__ == '__main__':
#     root = TrieNode('*', None)

    # for d in load_data():
    #     key, value = d.split(':', 1)
    #     key = key[1:-1]
    #     value = json.loads(value)
    #     # print(value)
    #     root.insert(key, value)


    # print(root.char)

    # root.insert('p2', ['street'], 'V')
    # root.insert('p2', ['licensePlate'], 's')
    # root.insert('p20', ['number', 'aek'], '308')
    # root.insert('p21', ['number'], '308')
    # root.insert('p201', ['name'], 'PLi')

    # r=(root.search('p7'))
    # print(r)
    # r=(root.search('p2'))
    # print(r)
    # r=(root.search('p20'))
    # print(r)
    # r=(root.search('p21'))
    # print(r)
    # r=(root.search('p23'))
    # print(r)
    # r=(root.search('p201', ['name']))
    # print(r)
    # r = (root.search('p201', ['na']))
    # print(r)
    # r = (root.search('p201', ['naml']))
    # print(r)
    # r = (root.search('p201', ['namel']))
    # print(r)

    # root.insert('p0', {"iban":"o","country":{"zip":{"secureCode":{"longitude":74.97272373480979,"email":"aah","secureCode":{"email":"unk","height":98.69482068289662,"name":"Ww"}},"street":"Xgl","country":"P"},"licensePlate":"YV","email":"vp"},"number":610})
    print('person0', test(root.find('person0')))
    print('person1', test(root.find('person1')))
    print('person2', test(root.find('person2')))
    print('person3', test(root.find('person3')))
    print('person4', test(root.find('person4')))
    print('person5', test(root.find('person5')))
    print('person6', test(root.find('person6')))
    print('person7', test(root.find('person7')))
    print('person8', test(root.find('person8')))
    print('person9', test(root.find('person9')))
    # print('person10', test(root.find('person10')))
    # print('person11', test(root.find('person11')))
    # print('person12', test(root.find('person12')))
    # print('person13', test(root.find('person13')))
    # print('person14', test(root.find('person14')))
    # print('person15', test(root.find('person15')))
    # print('person16', test(root.find('person16')))
    # print('person17', test(root.find('person17')))
    # print('person18', test(root.find('person18')))
    # print('person19', test(root.find('person19')))

    print(root.remove('person10'))
    print(root.remove('person1'))
    print(root.remove('person1'))
    print(root.remove('person11'))
    root.insert('person1', {"iban":"o","country":{"zip":{"secureCode":{"longitude":74.97272373480979,"email":"aah","secureCode":{"email":"unk","height":98.69482068289662,"name":"Ww"}},"street":"Xgl","country":"P"},"licensePlate":"YV","email":"vp"},"number":610})
    print('person1', test(root.find('person1')))
    # root.remove('person10')
    # print('person20', test(root.find('person20')))
    # print('person21', test(root.find('person21')))
    # print('person22', test(root.find('person22')))
    # print('person23', test(root.find('person23')))
    # print('person24', test(root.find('person24')))
    # print('person25', test(root.find('person25')))
    # print('person26', test(root.find('person26')))
    # print('person27', test(root.find('person27')))
    # print('person28', test(root.find('person28')))
    # print('person29', test(root.find('person29')))

    # r = root.find('person0.country.zip.secureCode')
    # root.insert('p1', ['street', 'height'], '53.193')
    # root.insert('p1', ['street', 'street'], 'LUyC')
    # root.insert('p1', ['birthdate'], '263')
    # root.insert('p1', ['iban'], 'vJt')
    # root.insert('p7a', ['phone'], 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA')
    # root.insert('p7', ['phone'], 'reA')
    # root.insert('p7', ['street', 'birthdate'], '531')
    # root.insert('p7', ['street', 'zip', 'number', 'number'], '475')
    # root.insert('p7', ['street', 'zip', 'number', 'iban'], 'I')
    # root.insert('p7', ['street', 'zip', 'number', 'secureCode'], '39')
    # #
    # print('p0', test(root.find('p0.email.iban.favoriteColor.licensePlate')))
    # print('person2.streeet', test(root.find('p2.streeet')))
    # print('person2.str', test(root.find('p2.str')))
    # print('person2', test(root.find('p2')))
    # print('person2.street', test(root.find('p2.street')))
    # print('person2.licensePlate', test(root.find('p2.licensePlate')))
    # # print('person2', test(root.find('p2.licensePlate')))
    # # print('person2.licensePlate', test(root.find('person2.licensePlate')))
    # # root.remove('person7')
    # # print('person7a', test(root.find('person7a')))
    # # root.insert('person7', ['phone'], 'reA')
    # print('person7', test(root.find('p7')))
    # print('person7.street.zip', test(root.find('p7.street.zip')))
    # print('person7.street.zip.number.iban', test(root.find('p7.street.zip.number.iban')))

    print('end')