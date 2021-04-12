import string


class Punctuation:

    @staticmethod
    def get():
        punctuation = set(string.punctuation)
        punctuation.remove('{')
        punctuation.remove('}')
        punctuation.remove(';')
        punctuation.remove('"')
        punctuation.remove('.')
        punctuation.remove(':')
        return punctuation
