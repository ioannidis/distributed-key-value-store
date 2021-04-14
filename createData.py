import argparse
import sys

from DataGenerator import DataGenerator

args_parser = argparse.ArgumentParser(description='kvServer')
args_parser.add_argument('-k', '--keyFile', dest='k', type=str, default='keyFile.txt', metavar='', required=True,
                         help='Contains the key, type pairs.')
args_parser.add_argument('-n', '--numberOfLines', dest='n', type=int, metavar='', required=True,
                         help='Indicates the number of lines.')
args_parser.add_argument('-d', '--nesting', dest='d', type=int, metavar='', required=True,
                         help='The maximum level of nesting.')
args_parser.add_argument('-m', '--numberOfKeys', dest='m', type=int, metavar='', required=True,
                         help='The maximum number of keys inside each value.')
args_parser.add_argument('-l', '--length', dest='l', type=int, metavar='', required=True,
                         help='The maximum length of a string value whenever you need to generate a string.')
args = args_parser.parse_args()

if args.n < 1:
    sys.exit('[Error] Number of lines should be greater than 0.')
elif args.d < 0:
    sys.exit('[Error] Nesting should be greater equal to 0.')
elif args.m < 0:
    sys.exit('[Error] The maximum number of keys inside each value should be greater equal to 0.')
elif args.l < 1:
    sys.exit('[Error] The maximum length of a string should be greater than 0.')

try:
    f = open(args.k, 'r')
    lines = f.readlines()
    f.close()
except FileNotFoundError as e:
    sys.exit(f'{e}')

keys = [(line.strip().split(' ')) for line in lines]

data_generator = DataGenerator(args, keys)
data_generator.generate()
data = data_generator.get_data()

f = open('dataToIndex.txt', 'w')
for d in data:
    f.write(d)
    f.write('\n')
f.close()



