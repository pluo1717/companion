import json
import csv
import glob
import re


json_dir = '北方工大伴随180720/'
json_file_paths = sorted(glob.glob(json_dir+'*.json'))[0:0]
print(json_file_paths)
# {"R":"04",
# "C":"37",
# "S":"0",
# "D":"",
# "U":"1531989362",
# "SI":"10000947",
# "F":"5",
# "X":"122734495",
# "I":"351664000_1",
# "Y":"31052278",
# "M":"351664000",
# "N":""},


save_dir = 'ncut180720/'

keys = ['R', 'C', 'S', 'D', 'U', 'SI', 'F', 'X', 'I', 'Y', 'M', 'N']
for path in json_file_paths:
    name = re.split('/|\.', path)[-2]
    with open(path) as rf:
        reader = json.load(rf)
        with open(save_dir + name + '.csv', 'w') as wf:
            writer = csv.writer(wf)
            writer.writerow(keys)
            for json_row in reader:
                csv_row = []
                for key in keys:
                    csv_row.append(json_row[key])
                writer.writerow(csv_row)


