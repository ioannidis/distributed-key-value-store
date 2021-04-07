import collections


class TrieNode:

    def __init__(self, char, value=None, is_key=False, is_root=False) -> None:
        self.children = collections.defaultdict(TrieNode)
        self.char = char
        self.value = value
        self.is_key = is_key
        self.is_root = is_root
        self.occurrences = 1

    def insert(self, key, levels={}):
        if not key:
            self.is_key = True
            if levels:
                if not self.value:
                    self.value = TrieNode('*', is_root=True)

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
                if self.value:
                    return self.value.search(levels[0], levels[1:])
                return

        if key[0] not in self.children:
            return

        return self.children[key[0]].search(key[1:], levels)

    def find_path(self, s):
        s = s.split('.')
        return self.search(s[0], s[1:])

    def find(self, s):
        return self.search(s)

    # Res builder pre-order
    def res_builder(self, s, branch, depth):

        if self.is_key:
            if isinstance(self.value, TrieNode):
                temp_s = s
                branch[temp_s] = {}
                self.value.res_builder('', branch[temp_s], depth + 1)
            else:
                branch[s] = self.value

        else:
            for k, c in self.children.items():
                c.res_builder(s + k, branch, depth)
