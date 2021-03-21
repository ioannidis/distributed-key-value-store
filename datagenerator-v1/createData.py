import collections
import getopt
import json
import sys

from dataGenerator import DataGenerator


available_options = "k:n:d:l:m:"
options = collections.defaultdict()
try:
    args, values = getopt.getopt(sys.argv[1:], available_options)

    for k, v in args:
        options[k[1:]] = v

except getopt.error as err:
    print(str(err))
    sys.exit(2)

print(options.items())

f = open(options['k'], 'r')
lines = f.readlines()
f.close()
keys = [(line.strip().split(' ')) for line in lines]

data_generator = DataGenerator(options, keys)
data_generator.generate()
data = data_generator.get_data()

f = open(options['k'], 'w')
for d in data:
    f.write(json.dumps(d)[1:-1])
    f.write('\n')
f.close()



