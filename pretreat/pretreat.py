import csv
import glob2
from re import split
from operator import itemgetter

# 原数据文件夹路径
files_dir = '../test_data/common/'

# 保存处理后的数据的文件夹路径
save_dir = 'common/'

# 原数据文件中的时间戳索引
time_index = 0

csv_files = sorted(glob2.glob(files_dir + '*.csv'))


def correct_time(data):
    print('时间需修正的数据：')
    ids = []
    for i in range(len(data)):
        try:
            a = int(data[i][time_index])
        except ValueError:
            ids.append(i)
            a = int(data[i-1][time_index]) * 2 - int(data[i - 2][time_index])
        data[i][time_index] = a
    print(ids)


def drop_repeated(data):
    print('重复的数据：')
    ids = []
    i = 1
    while i < len(data):
        if data[i-1][time_index] == data[i][time_index]:
            ids.append(data[i][time_index])
            del data[i]
        else:
            i += 1
    print(ids)


def add_id(data, id):
    print('添加id')
    for record in data:
        record.insert(0, id)


for f in csv_files:
    print(f)
    name = split('/|\.', f)[-2]
    with open(f) as rf:
        data = list(csv.reader(rf))

        # 修正时间
        correct_time(data)

        # 排序
        data = sorted(data, key=itemgetter(time_index))

        # 删除重复数据
        drop_repeated(data)

        # 添加船号
        add_id(data, name)

        with open(save_dir + name+'.csv', 'w') as wf:
            writer = csv.writer(wf)
            for recorder in data:
                writer.writerow(recorder)
