import csv
import re
import glob
from math import atan2, degrees


# 数据源文件夹路径
files_dir = '../interp1d/common/'

# 获取.csv文件
csv_files = sorted(glob.glob(files_dir+'*.csv'))

# 保存处理后的数据的文件夹路径
save_dir = 'common/'

# 源数据中经度的索引
lon_index = 2
# 源数据中纬度的索引
lat_index = 3


def add_cog(data):
    print('添加航向信息')
    degree = 0

    data[0].append(degree)

    for i in range(1, len(data)):
        # 根据两点的经纬度之差以及数学上的tan函数粗略求出航向
        dx = float(data[i][lon_index]) - float(data[i - 1][lon_index])
        dy = float(data[i][lat_index]) - float(data[i - 1][lat_index])

        degree = degrees(atan2(dy, dx)) % 360

        data[i].append(degree)


for f in csv_files:
    # 获取文件名
    name = re.split('/|\.', f)[-2]
    print(f)

    # 打开文件
    with open(f) as rf:
        # 读取数据，并且转换为一个list
        data = list(csv.reader(rf))

        # 添加航向
        add_cog(data)

        # 将数据保存下来
        with open(save_dir + name + '.csv', 'w') as wf:
            writer = csv.writer(wf)
            for i in data:
                writer.writerow(i)
