import csv
import time, datetime
import glob
import re
from operator import itemgetter
from math import atan2, degrees
from geopy.distance import vincenty
from scipy import interpolate


# 对哪个文件夹中的csv文件插值
files_dir = '../pretreat/common/'

# 插值后得到的csv文件的保存路径
save_dir = 'common/'

# 每隔多少秒插一条
gap_time = 300

# 超过多少秒不进行插入
no_interp = 3600

# 各项数据索引
time_index = 1
lon_index = 2
lat_index = 3

# 获取.csv文件路径，并且排序
csv_paths = sorted(glob.glob(files_dir + '*.csv'))

# 获取文件名，即船号，用于生成新的文件保存新的数据
csv_names = []
for path in csv_paths:
    name = re.split(r'/|\.', path)[-2]
    csv_names.append(name)


# 对时间戳进行插值，当相邻的两个时间戳大于NO_INTERP时不再他们之间进行插值
def get_new_time_arr(arr, gap):
    print('插值......')
    new_arr = []
    i = 0
    a = []
    print('差值大于NO_INTERP的序号和最后一组序号:')
    while i < len(arr):
        a.append(arr[i])
        i += 1
        # 将原先的时间戳列表进行分段，如果相邻两个时间戳之差大于no_interp就在两个时间戳中间砍一刀，
        if i == len(arr) or arr[i] - arr[i-1] > no_interp:
            # 主要用于输出相邻时间戳大于no_interp的数据序号
            print(i, i-1)
            # 把这一段时间戳列表的第一个添加上去
            new_arr.append(a[0])
            # 生成第一个数值是gap的整数倍的时间戳
            cur_time = a[0] + gap - a[0] % gap
            # 不断生成数值是gap的这数倍的时间戳，直至生成的时间戳大于这一段时间戳列表的最后一个
            while cur_time < a[-1]:
                new_arr.append(cur_time)
                cur_time += gap
            # 原先数据的这个时间段有多个数据，则把最后一个数据加上去
            if len(a) != 1:
                new_arr.append(a[-1])
            a = []
    return new_arr


# time_arr = [45, 445, 845, 1245, 5045, 5445]
# print(get_new_time_arr(time_arr, gap=GAP_TIME))


# 遍历所有文件
for path, name in zip(csv_paths, csv_names):
    # 打开文件
    with open(path) as rf:
        print(path)

        # 读取文件内容 并且转换为list
        data = list(csv.reader(rf))

        # 将data中的时间戳转换成int型，并且以列表的形式存储
        time_arr = [int(i[time_index]) for i in data]

        # 将data中的经度、纬度转换成float型，并且以列表的形式存储
        lon_arr = [float(i[lon_index]) for i in data]
        lat_arr = [float(i[lat_index]) for i in data]

        # 生成一个经度关于时间戳的函数
        f_lon = interpolate.interp1d(time_arr, lon_arr, kind='quadratic')
        # 生成一个纬度关于时间戳的函数
        f_lat = interpolate.interp1d(time_arr, lat_arr, kind='quadratic')

        # 获取新的时间戳列表
        new_time_arr = get_new_time_arr(time_arr, gap=gap_time)

        # 根据新的时间戳列表生成新的经纬度列表
        new_lon = f_lon(new_time_arr)
        new_lat = f_lat(new_time_arr)

        # 将船号与新生成的时间戳、经纬度保存下来
        with open(save_dir + name + '.csv', 'w') as wf:
            writer = csv.writer(wf)
            for i in range(len(new_time_arr)):
                record = []
                record.append(name)
                record.append(new_time_arr[i])
                record.append(new_lon[i])
                record.append(new_lat[i])
                writer.writerow(record)


