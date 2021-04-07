import sys
import tokenize


class Parser:

    @staticmethod
    def file_serializer(file):
        try:
            f = open(file, 'r')
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

        except FileNotFoundError as e:
            sys.exit(f'{e}')

    @staticmethod
    def serialize(s):
        return s.replace(';', ',')

    @staticmethod
    def deserialize(s):
        return s.replace(',', ';')
