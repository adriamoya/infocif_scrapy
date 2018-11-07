import os
import json
import pandas as pd

dirname = os.path.dirname(os.path.dirname(__file__))
input_file_path = "output/companies.json"
fullpath = os.path.join(dirname, input_file_path)

# Read data.
data = []
with open(fullpath) as input_file:
    print('---> Reading %s' % input_file_path)
    for line in input_file:
        data.append(json.loads(line))

df = pd.DataFrame(data)
# df.reset_index(inplace=True)
# df.drop('index', axis=1, inplace=True)
df.to_csv(input_file_path.replace('json', 'csv'), sep=';', encoding='utf-8', index=False)
print('---> CSV stored in ./%s' % input_file_path.replace('json', 'csv'))
