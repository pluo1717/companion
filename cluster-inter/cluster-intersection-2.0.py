import matplotlib.pyplot as plt
import glob
import sklearn.cluster as skc
import csv
import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from geopy.distance import vincenty

# 所有船在同一时刻的数据文件夹路径
data_dir = '../same_min/common_0110_0111/'

# 用来上图的数据文件夹
draw_dir = '../add_cog/common/'

# 一个簇中最少min_n_ship只船
min_n_ship = 2

# 相距max_dis，不再判断为伴随 单位：m
max_dis = 15 * 1000

# 当两只船的航向差大于max_dif_cog(单位：度)时，我们认为这两只船不是伴随
max_dif_cog = 45

# 持续duration（单位：s）才算伴随
min_duration = 3600

# 两次生成候选集的时间差（单位：s）
gap = 60 * 5

# 颜色集
colors = ['orange', 'green', 'blue', 'purple', '#223456']

full_track_colors = [(0.1, 0.1, 0.1), (0.32, 0.32, 0.32), (0.64, 0.64, 0.64), (0.96, 0.96, 0.96)]

# 获取伴随时各项数据索引
# 船号
id_index = 0
# 时间戳
time_index = 1
# 经度
lon_index = 2
# 纬度
lat_index = 3
# 方向
cog_index = 4


# 打印列表
def prt_list(list):
    for l in list:
        print(l)


# 定义一个表示簇的类
class Cluster:

    def __init__(self, ids, sta_time, duration):
        # ids表示这个簇中所有船的船号
        self.ids = set(ids)
        # sta_time表示形成这个簇的开始时间
        self.sta_time = sta_time
        # duration表示这个簇的持续时间
        self.duration = duration

    # 将簇的信息打印出来
    def prt(self):
        print(self.sta_time, '%dmin' % (self.duration//60), self.ids)

    # 判断self这个簇的ids是不是和clusters列表的簇的ids相等
    def in_clusters(self, clusters):
        for cluster in clusters:
            if self.ids == cluster.ids:
                return True
        return False

    # 画出ids的所有伴随段的轨迹
    def draw_other_same_ids_track(self, clusters, file_dir, data_sta_time, data_end_time):
        # ids大于2的只画出轨迹，不画伴随段
        if len(self.ids) > 2:
            self.draw_ids_full_track(clusters, file_dir, data_sta_time, data_end_time)
            return

        # 根据ids中的船号和files_dir获取文件路径
        file_paths = [file_dir + i + '.csv' for i in self.ids]
        dfs = []
        # 首先画出整条轨迹
        for i, fp in enumerate(file_paths):
            # 获取数据
            df = pd.read_csv(fp, header=None)
            # 获取（data_sta_tim <= 时间戳 <= data_end_time）的数据
            df = df[(df[time_index] >= data_sta_time) & (df[time_index] <= data_end_time)]

            # 获取经纬度
            lon = np.array(df[lon_index])
            lat = np.array(df[lat_index])

            # 将经纬绘制出来连城线
            plt.plot(lon, lat, color=full_track_colors[i % len(full_track_colors)], marker='.', linewidth=1)

            # 保留刚刚的用于绘制的数据，后面用来绘制伴随
            dfs.append(df)

        # 用于标记不同的颜色
        color_index = 0
        for c in clusters:
            if self.ids.issubset(c.ids):
                c.prt()
                for df in dfs:
                    # 获取这个簇从起始时间（sta_time）到截止时间（sta_time+duration）的数据
                    filtered_df = df[(df[time_index] >= c.sta_time) & (df[time_index] <= c.sta_time+c.duration)]
                    lon = np.array(filtered_df[lon_index])
                    lat = np.array(filtered_df[lat_index])

                    # 用不同的颜色画出不同的伴随段
                    plt.plot(lon, lat, color=colors[color_index % len(colors)], marker='.', linewidth=1)

                    # 用五角星标出起始点
                    plt.plot(lon[0], lat[0], color='red', marker='*')

                    # 在起始点注明起始时间
                    dateArray = datetime.datetime.utcfromtimestamp(c.sta_time)
                    text = dateArray.strftime("%Y-%m-%d %H:%M")
                    plt.text(lon[0], lat[0], str(text))

                    # 用三角形标出截止点
                    plt.plot(lon[-1], lat[-1], color='red', marker='>')

                    # 在截止点注明截止时间
                    dateArray = datetime.datetime.utcfromtimestamp(c.sta_time+c.duration)
                    text = dateArray.strftime("%Y-%m-%d %H:%M")
                    plt.text(lon[-1], lat[-1], str(text))

                # 控制使用不同的颜色
                color_index += 1
        plt.show()

    # 绘制这个簇中所有船只在这整段时间的轨迹
    def draw_ids_full_track(self, clusters, file_dir, data_sta_time, data_end_time):
        file_paths = [file_dir + i + '.csv' for i in self.ids]
        for i, fp in enumerate(file_paths):
            df = pd.read_csv(fp, header=None)
            df = df[(df[time_index] >= data_sta_time) & (df[time_index] <= data_end_time)]
            lon = np.array(df[lon_index])
            lat = np.array(df[lat_index])
            plt.plot(lon, lat, color=colors[i%len(colors)], marker='.', linewidth=1)
            plt.plot(lon[0], lat[0], color='red', marker='*')
        plt.show()


# 根据labels生成候选集，在生成候选集的过程中，通过data中的航向数据删除不符合的候选集
def get_cur_clusters(data, labels):
    n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
    clusters = []
    for index in range(n_clusters):
        ids = []
        cogs = []
        points = []
        # 把在同一个簇中的id、航向、经纬度保存一下
        for i in range(len(labels)):
            if labels[i] == index:
                ids.append(data[i][id_index])
                cogs.append(data[i][cog_index])
                points.append((data[i][lat_index], data[i][lon_index]))

        # 船只数量过少的簇不要
        if len(ids) < min_n_ship:
            continue

        # 两只船航向偏差太大的簇不要
        elif len(ids) == 2:
            dif_c = abs(float(cogs[0]) - float(cogs[1]))
            dif_c = dif_c if dif_c < 180 else 360-dif_c
            if dif_c > max_dif_cog:
                continue

        # 相距太远的不要
        continue_flag = False
        for i1 in range(len(points)):
            for i2 in range(i1+1, len(points)):
                dis = vincenty(points[i1], points[i2]).meters
                if dis > max_dis:
                    continue_flag = True
                    break
            if continue_flag:
                break
        if continue_flag:
            continue

        # 生成一个簇
        cluster = Cluster(ids, int(data[i][time_index]), 60)
        # 添加到当前时刻的簇群
        clusters.append(cluster)
    return clusters


# 对之前的候选集和当前时刻的候选集取交
def get_new_clusters(old_clusters, cur_clusters):
    new_clusters = []
    for cc in cur_clusters:
        for oc in old_clusters:
            if cc.ids.issubset(oc.ids):
                cc.duration = oc.duration + gap
                cc.sta_time = oc.sta_time
                break
            ids = set([i for i in oc.ids if i in cc.ids])
            if len(ids) >= min_n_ship:
                cluster = Cluster(ids, oc.sta_time, oc.duration+gap)
                new_clusters.append(cluster)
        new_clusters.append(cc)
    return new_clusters

# 根据file_paths提供的数据获取伴随，保存在companions中
def get_companions(file_paths, companions):
    old_clusters = []
    cur_clusters = []
    new_clusters = []
    for i in range(len(file_paths)):
        cfp = csv_file_paths[i]
        print('\n\n正在读取第%d个文件' % i, cfp)

        with open(cfp) as rf:
            data = np.array(list(csv.reader(rf)))

            # 密度聚类算法
            dbscan_data = data[:, [lon_index, lat_index, id_index]]
            db = skc.DBSCAN(eps=3, min_samples=2, metric='euclidean', n_jobs=4).fit(dbscan_data)

            labels = db.labels_
            print(labels)
            # 根据当前时刻所有船只的数据生成候选集cur_clusters
            cur_clusters = get_cur_clusters(data, labels)
            print('get_cur_clusters', len(cur_clusters))
            for cc in cur_clusters:
                cc.prt()

            # 当前时刻生成的候选集cur_clusters与原先存在的候选集old_clusters取交
            new_clusters = get_new_clusters(old_clusters, cur_clusters)
            print('get_new_clusters', len(new_clusters))
            for nc in new_clusters:
                nc.prt()

            # 如果原先存在候选集old_clusters中的簇不在新的候选集new_clusters中，说明这个簇已经结束了
            # 于是判断这个簇持续的时间是否大于最小持续时间min_duration，大于则判断为伴随
            for oc in old_clusters:
                if not oc.in_clusters(new_clusters):
                    if oc.duration > min_duration:
                        companions.append(oc)

            old_clusters = new_clusters

            # 对最后一个时刻生成的新的候选集进行特殊处理
            if i == len(file_paths)-1:
                for nc in new_clusters:
                    if nc.duration > min_duration:
                        companions.append(nc)


if __name__ == '__main__':

    companions = []
    csv_file_paths = sorted(glob.glob(data_dir + '*.csv'))

    # 获取数据的开始结束时间
    data_sta_time = 0
    data_end_time = 0
    print('##', csv_file_paths[0], print(csv_file_paths[-1]))
    with open(csv_file_paths[0]) as rf:
        data = list(csv.reader(rf))
        data_sta_time = int(data[0][1])
    with open(csv_file_paths[-1]) as rf:
        data = list(csv.reader(rf))
        data_end_time = int(data[0][1])

    # 获取伴随，伴随信息保存在companions
    get_companions(csv_file_paths, companions)

    print()
    for i, c in enumerate(companions):
        print('伴随', i, ':')
        c.prt()

    ids_set = []
    print(data_sta_time, data_end_time)

    for cluster in companions:
        # cluster.draw_full_track()
        if cluster.ids in ids_set:
            continue
        print(len(cluster.ids), '条轨迹')

        # 绘制伴随图
        cluster.draw_other_same_ids_track(companions, draw_dir, data_sta_time, data_end_time)
        ids_set.append(cluster.ids)

    print(len(ids_set))










