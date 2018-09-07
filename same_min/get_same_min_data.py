from scipy import interpolate
import csv
import re
import glob
import numpy as np
import time as tm
import datetime
from operator import itemgetter

# 添加航向后的数据的路径
files_dir = '../add_cog/common/'

# 数据保存路径
save_dir = 'common_0110_0111/'

# 时间段以及时间间隔，时间间隔的值的大小设置为插值算法中的时间间隔的整数倍
sta_time = '2017-01-10 00:00:00'
end_time = '2017-01-11 00:00:00'
interval = 5  # 单位：min

# 数据中的时间索引
time_index = 1

# 获取csv文件路径，并且排序
csv_paths = sorted(glob.glob(files_dir + '*.csv'))
print(csv_paths)

posi_list = []

# 读取所有的数据保存在posi_list列表中
for path in csv_paths:
    with open(path) as rf:
        posi = list(csv.reader(rf))
        posi_list.append(posi)

print("读取数据完毕！")

# 将起始日期与截止日期转换成时间戳，并且使时间戳为时间间隔的整数倍，由于中美相差八个时区，所以加上八个小时
arr = tm.strptime(sta_time, '%Y-%m-%d %H:%M:%S')
sta_stamp = tm.mktime(arr) - tm.mktime(arr)%(interval*60) + 8 * 3600
arr = tm.strptime(end_time, '%Y-%m-%d %H:%M:%S')
end_stamp = tm.mktime(arr) - tm.mktime(arr)%(interval*60) + 8 * 3600

# end_stamp = 1488297600

datetime_list = []
s = sta_stamp
# 按时间间隔和起止时间生成时间戳列表
while s <= end_stamp:
    # dt = datetime.datetime.utcfromtimestamp(s).strftime("%Y%m%d%H%M%S")
    # print(dt)
    datetime_list.append(s)
    s += 60 * interval

for dt in datetime_list:
    # 根据时间戳转生成日期字符串，这个字符串用作文件名
    name = datetime.datetime.utcfromtimestamp(dt).strftime("%Y%m%d%H%M%S")[:-2]
    # 生成一个以日期为名字的文件
    with open(save_dir + name + '.csv', 'w') as wf:
        same_min_data = []
        print('创建'+name+'文件', dt)
        writer = csv.writer(wf)
        # 获取各个船只在该时间戳的数据
        for posi in posi_list:
            i = 0
            while i < len(posi):
                if int(posi[i][time_index]) == dt:
                    same_min_data.append(posi[i])
                    del posi[i]
                    break
                i += 1
        # 将获取的数据写入一日期为名的文件
        for i in same_min_data:
            writer.writerow(i)
print('done!')

