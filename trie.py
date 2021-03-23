import collections


class TrieNode:

    def __init__(self, char, value=None, is_key=False) -> None:
        self.children = collections.defaultdict(TrieNode)
        self.char = char
        self.value = value
        self.is_key = is_key

    def insert(self, key, levels=[], value=None):
        if not key:
            self.is_key = True
            if levels:
                if not self.value:
                    self.value = TrieNode('*')
                self.value.insert(levels[0], levels[1:], value)
            else:
                self.value = value
            return

        c = key[0]
        if c in self.children:
            node = self.children[c]
            node.insert(key[1:], levels, value)
        else:
            self.children[c] = TrieNode(c)
            self.children[c].insert(key[1:], levels, value)

    def remove(self, key):
        if not key:
            if self.is_key:
                self.value = None
                self.is_key = False
                return True
            return False

        c = key[0]
        if c in self.children:
            return self.children[c].remove(key[1:])

        return False

    def search(self, key, levels=[]):

        if not key:
            if not self.is_key:
                return

            if not levels:
                if self.is_key:
                    return self.value
                return
            else:
                return self.value.search(levels[0], levels[1:])

        if key[0] not in self.children:
            return

        return self.children[key[0]].search(key[1:], levels)

    def find(self, s):
        s = s.split('.')
        return self.search(s[0], s[1:])

    # Res builder pre-order
    def res_builder(self, node, s, branch, depth):

        if node.is_key:
            if isinstance(node.value, TrieNode):
                temp_s = s
                self.res_builder(node.value, temp_s + ':{', branch, depth + 1)
            else:
                temp_s = s
                temp_s += ':'+node.value + '}' * depth
                branch.append(temp_s)

        else:
            for k, c in node.children.items():
                self.res_builder(c, s + k, branch, depth)


def test(node):
    res = []
    if not node:
        return

    if isinstance(node, str):
        res.append(node)
    else:
        # if node.char == '*':
        for k, c in node.children.items():
            b = []
            root.res_builder(c, k, b, 0)
            res.append(b)

    return res

if __name__ == '__main__':
    root = TrieNode('*', None, float('inf'))
    # print(root.char)

    root.insert('p2', ['street'], 'V')
    root.insert('p2', ['licensePlate'], 's')
    root.insert('p20', ['number', 'aek'], '308')
    root.insert('p21', ['number'], '308')
    root.insert('p201', ['name'], 'PLi')

    # r=(root.search('p7'))
    # print(r)
    r=(root.search('p2'))
    print(r)
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

    root.insert('p1', ['street', 'height'], '53.193')
    root.insert('p1', ['street', 'street'], 'LUyC')
    root.insert('p1', ['birthdate'], '263')
    root.insert('p1', ['iban'], 'vJt')
    root.insert('p7a', ['phone'], 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA')
    root.insert('p7', ['phone'], 'reA')
    root.insert('p7', ['street', 'birthdate'], '531')
    root.insert('p7', ['street', 'zip', 'number', 'number'], '475')
    root.insert('p7', ['street', 'zip', 'number', 'iban'], 'I')
    root.insert('p7', ['street', 'zip', 'number', 'secureCode'], '39')
    #
    print('panos', test(root.find('panos')))
    print('person2.streeet', test(root.find('p2.streeet')))
    print('person2.str', test(root.find('p2.str')))
    print('person2', test(root.find('p2')))
    print('person2.street', test(root.find('p2.street')))
    print('person2.licensePlate', test(root.find('p2.licensePlate')))
    # print('person2', test(root.find('p2.licensePlate')))
    # print('person2.licensePlate', test(root.find('person2.licensePlate')))
    # root.remove('person7')
    # print('person7a', test(root.find('person7a')))
    # root.insert('person7', ['phone'], 'reA')
    print('person7', test(root.find('p7')))
    print('person7.street.zip', test(root.find('p7.street.zip')))
    print('person7.street.zip.number.iban', test(root.find('p7.street.zip.number.iban')))

    print('end')