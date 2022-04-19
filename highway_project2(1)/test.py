import copy
import time

import numpy as np
import scipy
from scipy import optimize

def is_cross_match(record_k, record_v, info_car, k_type):
    def judge_condition_cross(x, y):
        flag = False
        if len(x) == 0:
            return False
        if 1000 * _max_time_limited * 20 > x[_t] - y[_t] >= _min_time_limited * 1000 and (
                x[_scope][0] <= y[_scope][1] <=
                x[_scope][1] or x[_scope][0] <=
                y[_scope][0] < x[_scope][1] or y[_scope][0] < x[_scope][1] <= y[_scope][1]):
            flag = True  # 判断预测条件
        return flag

    def judge_condition_small(x, y):
        if len(x) == 0:
            return False
        # if x[_car_type]==0:
        #     if y[_car_type]!=0:
        #         return False
        if y[_car_type] == 0 and (
                x[_scope][0] <= y[_scope][1] <=
                x[_scope][1] or x[_scope][0] <=
                y[_scope][0] < x[_scope][1] or y[_scope][0] < x[_scope][1] <= y[_scope][1]):
            return False

        if 1000 * _max_time_limited * 20 > x[_t] - y[_t] >= _min_time_limited * 1000 and (
                (x[_p] - y[_p]) / (x[_t] - y[_t])) * y[_v] > 0:
            # 判断预测条件
            return True

    def is_info_cross(x, y):
        if x == y:
            return False
        if len(x) == 0 or len(y) == 0:
            return False
        if x[_ch] == y[_ch] and (x[_scope][0] <= y[_scope][1] <=
                                 x[_scope][1] or x[_scope][0] <=
                                 y[_scope][0] < x[_scope][1] or y[_scope][0] < x[_scope][1] <= y[_scope][1]):
            return True
        return False

    # 去点大车旁边车道的定位点
    # for i in range(len(k_type)):
    #     if k_type[i] == 1:
    #         for j in range(len(info_car)):
    #             if judge_condition_cross(info_car[j], record_v[i]) and abs(info_car[j][_ch] - record_v[i][_ch])==1:
    #                 info_car[j] = []

    # 匹配同车道
    for i in range(len(info_car)):
        for j in range(len(info_car)):
            if is_info_cross(info_car[i], info_car[j]):
                print("范围有重叠", info_car[i], info_car[j])
                info_car[j] = []

    for i in range(len(info_car)):
        for j in range(len(record_v)):
            if judge_condition_cross(info_car[i], record_v[j]) and record_v[j][_ch] == info_car[i][_ch]:
                if ((info_car[i][_p] - record_v[j][_p]) / (info_car[i][_t] - record_v[j][_t])) * record_v[j][
                    _v] >= 0:
                    if info_car[i][_p] - record_v[j][_p] != 0:
                        print("交叉匹配同车道" + "车辆" + str(record_k[j]) + "位置从" + str(record_v[j][_p]) + '变为' + str(
                            info_car[i][_p]), info_car[i])
                        info_car[i].append(record_v[j][_v])
                        record_v[j] = info_car[i]
                    else:
                        print("位置重复出现,只更新时间", info_car[i], record_v[j])
                        record_v[j][_t] = info_car[i][_t]

                else:
                    if record_v[j][_p] < start:
                        print("在起始区域出现位置后退", info_car[i], record_v[j])
                    else:
                        print("交叉匹配同车道出现位置倒退，只更新时间", record_v[j], info_car[i])
                    record_v[j][_t] = info_car[i][_t]
                info_car[i] = []
                break

    for i in range(len(info_car)):
        small_distance = 40
        small_index = -1
        for j in range(len(record_v)):
            if judge_condition_small(info_car[i], record_v[j]) and record_v[j][_ch] == info_car[i][_ch]:
                if abs(info_car[i][_p] - record_v[j][_p]) < small_distance * ((
                                                                                      info_car[i][_t] - record_v[j][
                                                                                  _t] + 1000) // 1000):
                    small_distance = abs(info_car[i][_p] - record_v[j][_p])
                    small_index = j
        if small_index != -1:
            print(
                "相邻匹配同车道" + "车辆" + str(record_k[small_index]) + "位置从" + str(record_v[small_index][_p]) + '变为' + str(
                    info_car[i][_p]), info_car[i])
            info_car[i].append(record_v[small_index][_v])
            record_v[small_index] = info_car[i]
            info_car[i] = []

    for i in range(len(info_car)):
        small_distance = 40
        small_index = -1
        for j in range(len(record_v)):
            if judge_condition_small(info_car[i], record_v[j]):
                if info_car[i][_car_type] == 1 and record_v[j][_car_type] == 0:
                    continue
                elif info_car[i][_t] - record_v[j][_t] < 2.2 * _max_time_limited * 1000 and record_v[j][_car_type] == 0:
                    continue
                else:
                    if abs(record_v[j][_ch] - info_car[i][_ch]) == 1 and record_v[j][_p] > start:
                        if abs(info_car[i][_p] - record_v[j][_p]) < small_distance:
                            small_distance = abs(info_car[i][_p] - record_v[j][_p])
                            small_index = j

        if small_index != -1:
            distance_flag = True
            for n in range(len(record_v)):
                if small_index != n:
                    if (info_car[i][_p] - record_v[n][_p]) * (record_v[small_index][_p] - record_v[n][_p]) < 0:
                        print("相邻匹配出现位置重叠", info_car[i], record_v[small_index], record_v[n])
                        info_car[i] = []
                        distance_flag = False
                        break
            #
            if distance_flag and road_change[small_index] > 1:
                print("相邻匹配相邻车道" + '通道' + str(record_v[small_index][_ch]) + "变为" + str(info_car[i][_ch]),
                      "车辆" + "位置从" + str(record_v[small_index][_p]) + '变为' + str(info_car[i][_p]), info_car[i])
                info_car[i].append(record_v[small_index][_v])
                record_v[small_index] = info_car[i]
                road_change[small_index] = 0
                info_car[i] = []
            else:
                road_change[small_index] += 1
    return record_k, record_v, info_car


def is_path_judge(former_record_v, new_record_v):
    def is_average_position(y, y_time):
        x = (np.array(y_time) - y_time[0]) / 1000
        n = scipy.optimize.curve_fit(lambda t, a, b: a + b * t, x, y)
        predict_value = []
        for i in x:
            predict_value.extend([abs(n[0][0] + n[0][1] * i)])
        ave_pos = []
        ave_time = []
        for i in range(len(predict_value) - 1):
            ave_pos.append(predict_value[i + 1] - predict_value[i])
            ave_time.append(x[i + 1] - x[i])
        ave_speed = 0
        for i in range(len(ave_pos)):
            ave_speed += ave_pos[i] / ave_time[i]
        return ave_speed / len(ave_pos) if ave_speed / len(ave_pos) > 5 else 5

    new_index = []
    for new_location in range(len(new_record_v)):
        if former_record_v[new_location] != new_record_v[new_location] and former_record_v[new_location][_ch] == \
                new_record_v[new_location][_ch]:
            new_index.append(new_location)
    if len(new_index) > 0:
        print("#####", former_record_v, new_index)
        for i in new_index:
            for j in range(len(new_record_v)):
                if i != j and former_record_v[j][_ch] == new_record_v[j][_ch] == new_record_v[i][_ch] == \
                        former_record_v[i][_ch]:
                    if former_record_v[i][_p] < former_record_v[j][_p] <= new_record_v[j][_p] < new_record_v[i][_p] or \
                            new_record_v[i][_p] < new_record_v[j][_p] <= former_record_v[j][_p] < former_record_v[i][
                        _p] and new_record_v[i][_t] - new_record_v[j][_t] < 1000:
                        tmp = new_record_v[j]
                        new_record_v[j] = new_record_v[i]
                        new_record_v[i] = tmp
                        print("位置匹配错误，已更改", tmp, "改为", new_record_v[j])

    for i in range(len(new_record_v)):
        if new_record_v[i] != former_record_v[i]:
            print("^^^^", line_change)
            if new_record_v[i][_ch] != former_record_v[i][_ch]:  # 变道
                line_change[i].append(copy.deepcopy(former_record_v))  # 存入变道之前所有车辆0位置
                line_change[i].append(copy.deepcopy(former_record_v[i]))  # 存入变道之前位置
                line_change[i].append(i)  # 变道车索引
                line_change[i].append(kType[i])  # 变道车的车型
                line_change[i].append(k)  # 存入变道点所有车辆信息
                line_change[i].append(kType)  # 存入变道点所有车辆车型
                line_change[i].append(copy.deepcopy(new_record_v[i]))  # 存入第一个点进行更新

            if len(line_change[i]) > 0:
                latest_index = -1
                latest_value = 50

                if len(line_change[i]) > 10:
                    car_position_count = 0
                    for history_car_position in line_change[i][0]:
                        print("%%",car_position_count, len(line_change[i][0]), len())
                        print(line_change[i][5][car_position_count])
                        if line_change[i][3] == 0 and history_car_position[_ch] == \
                                line_change[i][1][_ch] and line_change[i][5][car_position_count] == 1:  # 小车变成大车
                            if abs(history_car_position[_p] - line_change[i][1][_p]) < latest_value:
                                latest_value = abs(history_car_position[_p] - line_change[i][1][_p])
                                latest_index = car_position_count
                        elif line_change[i][3] == 1 and abs(
                                history_car_position[_ch] - line_change[i][1][_ch]) == 1 and line_change[i][5][
                            car_position_count] == 0:  # 找不同道上是否有车为小车(变道出现异常为小车占了大车的道)
                            if abs(history_car_position[_p] - line_change[i][1][_p]) < latest_value:
                                latest_value = abs(history_car_position[_p] - line_change[i][1][_p])
                                latest_index = car_position_count
                        car_position_count += 1  # 自增点确定车辆


                    car_info_flag = False
                    record_latest_index = latest_index  # 被纠正的车的历史索引

                    for car_info in range(len(k)):
                        if line_change[i][4][latest_index] == k[car_info]:
                            latest_index = car_info  # 被纠正的车被更新为现在的索引
                            if car_info_flag:
                                print("出现错误，多次匹配！！！")
                            car_info_flag = True

                    if car_info_flag:
                        print("被初始匹配到的车辆仍然在轨迹中", k, k[latest_index], line_change[i][4])
                    else:
                        print("被匹配到的车辆已经被移除了，没有轨迹信息", k, line_change[i][4][latest_index], line_change[i][4])

                    if line_change[i][3] == 0 and car_info_flag:
                        if latest_value != 50:
                            print("小车变道出现错误", "小车变道点为", line_change[i][1], "小车已经行驶到",
                                  line_change[i][-1]
                                  , "最近的大车历史位置为", line_change[i][0][record_latest_index], '最近大车已经行驶到',
                                  new_record_v[latest_index])
                            car_position_tmp = new_record_v[i]  # 错误车辆定位
                            new_record_v[i] = new_record_v[latest_index]
                            new_record_v[latest_index] = car_position_tmp
                            print("位置纠正，清空变道信息")
                            # print("最近的大车已经行驶出范围，被移除", "历史记录定位点为", line_change[i][0], "最新的定位点为", new_record_v)
                            line_change[i] = []
                            break
                        else:
                            print("小车变道点出现问题，没有找到合适的点进行纠正", line_change[i][1], "小车已经行驶到",
                                  line_change[i][-1],
                                  "变道点所有车辆信息为", line_change[i][0])

                    if line_change[i][3] == 1 and len(
                            line_change[i]) > 13 and car_info_flag:  # 大车变小车, 条件较严格一点
                        if latest_value != 50:
                            print("大车变道出现错误", "大车变道点为", line_change[i][1], "大车已经行驶到",
                                  line_change[i][-1]
                                  , "最近的小车历史位置为", line_change[i][0][record_latest_index], '最近小车已经行驶到',
                                  new_record_v[latest_index])
                            car_position_tmp = new_record_v[i]  # 错误车辆定位
                            new_record_v[i] = new_record_v[latest_index]
                            new_record_v[latest_index] = car_position_tmp
                            print("位置纠正，清空变道信息")

                            # print("最近的小车已经行驶出范围，被移除", "历史记录定位点为", line_change[i][0], "最新的定位点为", new_record_v)
                            line_change[i] = []
                            break
                        else:
                            print("大车变道点出现问题，没有找到合适的点进行纠正", line_change[i][1], "大车已经行驶到",
                                  line_change[i][-1], "变道点所有车辆信息为", line_change[i][0])

                if len(line_change[i]) > 0 and new_record_v[i] != line_change[i][-1] and new_record_v[i][_car_type] != \
                        line_change[i][3]:  # 车型不一致
                    time_remove_list = []
                    for time_index in range(len(line_change[i])):
                        if time_index > 5 and new_record_v[i][_t] - line_change[i][time_index][_t] > 2000:  # 大于2s移掉
                            time_remove_list.append(line_change[i][time_index])

                    print("$$$", line_change)
                    print("$$$", i)
                    print("$$$", new_record_v)
                    for _remove_position in time_remove_list:
                        line_change[i].remove(_remove_position)

                    line_change[i].append(copy.deepcopy(new_record_v[i]))
                    if new_record_v[i][_t] - line_change[i][1][_t] > 5000:
                        print("变道时间超过了10s仍符合条件，清空此次变道信息")
                        line_change[i] = []

            # vDeleteTime[i] = time.time() * 1000
            # car_his_pos[i].append(copy.deepcopy(new_record_v[i][_p]))
            # car_his_pos_time[i].append(copy.deepcopy(new_record_v[i][_t]))
            # if len(car_his_pos[i]) >= 10:
            #     new_record_v[i][_v] = is_average_position(np.array(car_his_pos[i][-10:]), car_his_pos_time[i][-10:])
            # else:
            #     print('没有存够位置进行速度更新', car_his_pos[i], car_his_pos_time[i])


map_data = []
# 预备初始化的记录
carStack = []
# 已使用过的record
usedRecord = []
# 车的个数
car_num = 0
# 初始化最小距离
threshold = 20
# 初始化攒点个数
initialNum = 1
# 攒点删除时间
deleteZanDian = 1000
# 删除车辆时间
timeThreshold = 5000
# 栈时间
stackTime = 1000
k = []
v = []
kType = []
_ch = 0  # 通道号
_p = 1  # 位置
_max = 2
_scope = 3  # 范围
_t = 5  # 时间
_car_type = 4
_v = 6
_max_time_limited = 0.2  # 0.5滑窗设为0.5  0.1设为0.1
_min_time_limited = 0.01  # 0.5滑窗设为0.3  0.1设为0.05, 0.2设为0.01
# v
vTime = 5  # v中存放时间的索引
vSpeed = 6  # v中存放速度的索引
vPosition = 1  # v中存放定位的索引
vScope = 3  # v中存放范围的索引
vCartype = 4  # v中存放车型的索引
vTongDao = 0  # v中存放车型的索引
# car
cCartype = 4  # car中存放车型的索引
cTime = 5  # car中存放时间的索引
cPotition = 1  # car中存放定位的索引
cScope = 3  # car中存放范围的索引
cTongDao = 0  # car中存放通道的索引
pushT = 0
car = []
vDeleteTime = []
cStackDeleteTime = []
t = 0
# 车辆入口
start = 10048
end = 9998
entrance = [i for i in range(end, start)]
car_his_pos = []
car_his_pos_time = []
line_change = []
road_change = []
zhiXingDu = 0.89
chuKou = 10698
foreCastAndBianDaoStack = []
zanDianNeedNum = 1
zanDianThreshold = 35

line_change = [[], [[[3, 10683, 0.5446525812149048, [10673, 10693], 0, 1650084035206, 16.05404204197249],
                     [3, 10648, 0.5032823085784912, [10638, 10653], 0, 1650084035206, 18.000147481695404],
                     [3, 10622, 0.4278331398963928, [10617, 10627], 0, 1650084034833, 6.945462530783436],
                     [2, 10592, 1.3289210796356201, [10582, 10597], 1, 1650084035206, 8.784302518277384],
                     [3, 10607, 0.44040027260780334, [10602, 10612], 0, 1650084035206, 13.667083991573946],
                     [3, 10582, 0.44150787591934204, [10572, 10587], 0, 1650084035206, 5],
                     [3, 10567, 2.1867618560791016, [10562, 10572], 1, 1650084033713, 26.668009152297508],
                     [3, 10557, 0.2135966271162033, [10547, 10562], 0, 1650084035206, 29.105246361281484]],
                    [3, 10622, 0.4278331398963928, [10617, 10627], 0, 1650084034833, 6.945462530783436], 2, 0,
                    [2, 3, 4, 5, 6, 7, 8], [0, 0, 1, 0, 0, 0, 0],
                    [2, 10638, 0.7301236391067505, [10632, 10643], 0, 1650084035397, 6.945462530783436],
                    [2, 10678, 3.663438320159912, [10673, 10688], 1, 1650084036522, 18.27088811885872],
                    [2, 10683, 3.0290801525115967, [10678, 10688], 1, 1650084036708, 22.00848619917504],
                    [2, 10683, 3.0290801525115967, [10678, 10688], 1, 1650084036901, 25.570145252802263],
                    [2, 10698, 1.552635669708252, [10693, 10703], 1, 1650084037090, 29.722209562901426]], [], [], [],
               [], []]

v = [[3, 10693, 0.6802340745925903, [10683, 10698], 0, 1650084037090, 9.666873048350192],
     [2, 10698, 1.552635669708252, [10693, 10703], 1, 1650084037090, 22.143977414943148],
     [2, 10643, 0.3686780631542206, [10638, 10648], 0, 1650084037090, 18.03545129791321],
     [3, 10632, 1.8428388833999634, [10627, 10643], 1, 1650084037090, 21.460379932972693],
     [3, 10607, 2.8283660411834717, [10602, 10612], 1, 1650084037090, 7.081178885796153],
     [3, 10582, 0.7694551944732666, [10572, 10587], 0, 1650084037090, 7.465456279675307],
     [3, 10567, 0.806239902973175, [10562, 10572], 0, 1650084037090, 5.391330812861508]]
car = [[1, 0, 0, [0, 0], 0, 1650084037276], [2, 10693, 1.3183685541152954, [10688, 10698], 1, 1650084037276],
       [2, 10612, 2.0545318126678467, [10607, 10622], 1, 1650084037276],
       [3, 10718, 0.2800828814506531, [10713, 10728], 0, 1650084037276],
       [3, 10698, 1.5462729930877686, [10693, 10703], 1, 1650084037276],
       [3, 10653, 0.15914073586463928, [10648, 10658], 0, 1650084037276],
       [3, 10632, 1.0945520401000977, [10622, 10643], 1, 1650084037276],
       [3, 10607, 1.4855961799621582, [10602, 10612], 1, 1650084037276],
       [3, 10592, 0.5735692977905273, [10587, 10602], 0, 1650084037276],
       [3, 10572, 1.1671345233917236, [10562, 10577], 1, 1650084037276],
       [3, 10028, 0.15297366678714752, [10018, 10033], 0, 1650084037276],
       [3, 10008, 0.1391916126012802, [10003, 10013], 0, 1650084037276],
       [3, 9782, 0.33838847279548645, [9767, 9802], 0, 1650084037276]]
kType = [0, 0, 0, 1, 1, 0, 0]
k = [1, 2, 3, 4, 5, 6, 7]
former_v = copy.deepcopy(v)
is_cross_match(k, v, car, kType)
new_record_v = v
is_path_judge(former_v,new_record_v)

