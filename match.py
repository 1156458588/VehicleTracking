# info_car [[ch,p,scope,t, maxValue, carType]]
# -record_v = [[ch, p,scope,t,v]]
# scope = [min,max]
import sys
import threading
import time
import uuid
import copy, scipy
from scipy import optimize

import numpy as np
import pandas as pd
import random
from ZMQServer import MessageServer
from ZMQPublish import MessagePublisher
from Coodingdata import RoadEncoder


def getClean(y):
    d = []
    y.sort(reverse=True)
    for v in y:
        d.append(v[1])
    d = np.unique(d)
    maxV = []
    maxK = []
    for value in y:
        if value[1] in d and len(maxV) < len(d) and value[1] not in maxK:
            # 存放最大概率
            maxV.append(value[0])
            # 存放最大概率car索引
            maxK.append(value[1])
    return maxK, maxV


def is_cross_match(record_k, record_v, info_car, k_type):
    def judge_condition_cross(x, y):
        flag = False
        if len(x) == 0:
            return False
        # if x[_car_type]!=y[_car_type]:
        #     return False
        if 2000 > x[_t] - y[_t] >= _min_time_limited * 1000 and (
                x[_scope][0] <= y[_scope][1] <=
                x[_scope][1] or x[_scope][0] <=
                y[_scope][0] < x[_scope][1] or y[_scope][0] < x[_scope][1] <= y[_scope][1]):
            flag = True  # 判断预测条件
        return flag

    def judge_condition_small(x, y):
        if len(x) == 0:
            return False
        # if x[_car_type]!=y[_car_type]:
        #     return False
        # if x[_car_type]==0:
        #     if y[_car_type]!=0:
        #         return False
        if y[_car_type] == 0 and (
                x[_scope][0] <= y[_scope][1] <=
                x[_scope][1] or x[_scope][0] <=
                y[_scope][0] < x[_scope][1] or y[_scope][0] < x[_scope][1] <= y[_scope][1]):
            return False

        if 2000 > x[_t] - y[_t] >= _min_time_limited * 1000 and (
                (x[_p] - y[_p]) / (x[_t] - y[_t])) * y[_v] > 0:
            # 判断预测条件
            return True

    def is_info_cross(x, y):
        if len(x) == 0 or len(y) == 0:
            return False
        if x == y or (x[_p] < start and y[_p] < start):
            return False
        if x[_ch] == y[_ch] and (x[_scope][0] < y[_scope][1] <
                                 x[_scope][1] or x[_scope][0] <
                                 y[_scope][0] < x[_scope][1] or y[_scope][0] < x[_scope][1] < y[_scope][1]):
            return True
        return False

    # 去点大车旁边车道的定位点
    # for i in range(len(k_type)):
    #     if k_type[i] == 1:
    #         for j in range(len(info_car)):
    #             if judge_condition_cross(info_car[j], record_v[i]) and abs(info_car[j][_ch] - record_v[i][_ch])==1:
    #                 info_car[j] = []

    # 匹配同车道
    # for i in range(len(info_car)):
    #     for j in range(len(info_car)):
    #         if is_info_cross(info_car[i], info_car[j]):
    #             print("范围有重叠", info_car[i], info_car[j])
    #             info_car[j] = []

    for i in range(len(info_car)):
        tmp_cross_car = []
        for j in range(len(record_v)):
            if judge_condition_cross(info_car[i], record_v[j]) and record_v[j][_ch] == info_car[i][_ch]:
                tmp_cross_car.append(j)

        latest_cross_time_index = -1
        if len(tmp_cross_car) == 1:
            latest_cross_time_index = tmp_cross_car[0]

        elif len(tmp_cross_car) > 1:
            latest_cross_time = 2000
            for j in tmp_cross_car:
                if record_v[j][_t] - info_car[i][_t] < latest_cross_time:
                    latest_cross_time = info_car[i][_t] - record_v[j][_t]
                    latest_cross_time_index = j
            is_single_cross[latest_cross_time_index] = False
            print("多辆车可以交叉匹配，匹配最近时间的历史定位,最小时间差为", latest_cross_time)

        j = latest_cross_time_index
        if j != -1:
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
                    print("车型判断不一致", info_car[i], record_v[j])
                    continue
                elif info_car[i][_t] - record_v[j][_t] < 320 and record_v[j][_car_type] == 0:
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
            if distance_flag and road_change[small_index] >= 1:
                print("相邻匹配相邻车道" + '通道' + str(record_v[small_index][_ch]) + "变为" + str(info_car[i][_ch]),
                      "车辆" + "位置从" + str(record_v[small_index][_p]) + '变为' + str(info_car[i][_p]), info_car[i])
                info_car[i].append(record_v[small_index][_v])
                record_v[small_index] = info_car[i]
                road_change[small_index] = 0
                info_car[i] = []
            else:
                info_car[i] = []
                road_change[small_index] += 1
    return record_k, record_v, info_car


def is_path_judge(former_record_v, new_record_v):
    def is_average_position(y, y_time):
        tmp_y = 0
        for i in y:
            tmp_y += i - y[0]
        if tmp_y == 0:
            return 15
        x = (np.array(y_time) - y_time[0]) / 1000
        n = scipy.optimize.curve_fit(lambda t, a, b: a + b * t, x, y)
        predict_value = []
        for i in x:
            predict_value.extend([abs(n[0][0] + n[0][1] * i)])
        ave_pos = []
        ave_time = []
        for i in range(len(predict_value) - 1):
            ave_pos.append(predict_value[i + 1] - predict_value[i])
            ave_time.append(abs(x[i + 1] - x[i]))
        ave_speed = 0
        for i in range(len(ave_pos)):
            if ave_pos[i] != 0 and ave_time[i] != 0:
                ave_speed += ave_pos[i] / ave_time[i]
        return ave_speed / len(ave_pos)

    new_index = []
    for new_location in range(len(new_record_v)):
        if former_record_v[new_location] != new_record_v[new_location] and former_record_v[new_location][_ch] == \
                new_record_v[new_location][_ch]:
            new_index.append(new_location)
    if len(new_index) > 0:
        print("#####", former_record_v, new_index)
        for i in new_index:
            for j in range(len(new_record_v)):
                if i != j and is_single_cross[i] and former_record_v[j][_ch] == new_record_v[j][_ch] == new_record_v[i][
                    _ch] == \
                        former_record_v[i][_ch]:
                    if (former_record_v[i][_p] < former_record_v[j][_p] <= new_record_v[j][_p] < new_record_v[i][_p] and
                        new_record_v[i][_t] - new_record_v[j][_t] < 2000) or \
                            new_record_v[i][_p] < new_record_v[j][_p] <= former_record_v[j][_p] < former_record_v[i][
                        _p]:
                        tmp = new_record_v[j]
                        new_record_v[j] = new_record_v[i]
                        new_record_v[i] = tmp
                        print("位置匹配错误，已更改", tmp, "改为", new_record_v[j])

    for i in range(len(new_record_v)):
        print("&&", car_his_pos[i])
        if new_record_v[i] != former_record_v[i]:
            vDeleteTime[i] = time.time() * 1000
            car_his_pos[i].append(copy.deepcopy(new_record_v[i][_p]))
            car_his_pos_time[i].append(copy.deepcopy(new_record_v[i][_t]))
            if len(car_his_pos[i]) >= 10:
                new_record_v[i][_v] = is_average_position(np.array(car_his_pos[i][-10:]), car_his_pos_time[i][-10:])
            else:
                print('没有存够位置进行速度更新', car_his_pos[i], car_his_pos_time[i])

            print("^^^^", line_change)
            if new_record_v[i][_ch] != former_record_v[i][_ch]:  # 变道
                if len(line_change[i]) != 0:
                    print("历史变道信息未被清除", line_change, new_record_v[i])
                    line_change[i] = []
                line_change[i].append(copy.deepcopy(former_record_v))  # 存入变道之前所有车辆0位置
                line_change[i].append(copy.deepcopy(former_record_v[i]))  # 存入变道之前位置
                line_change[i].append(i)  # 变道车索引
                line_change[i].append(kType[i])  # 变道车的车型
                line_change[i].append(copy.deepcopy(k))  # 存入变道点所有车辆信息
                line_change[i].append(copy.deepcopy(kType))  # 存入变道点所有车辆车型
                line_change[i].append(copy.deepcopy(new_record_v[i]))  # 存入第一个点进行更新

            if len(line_change[i]) > 0:
                latest_index = -1
                latest_value = 50

                if len(line_change[i]) > 10:
                    car_position_count = 0
                    for history_car_position in line_change[i][0]:
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

                if len(line_change[i]) > 0 and new_record_v[i][_t] - line_change[i][1][_t] > 5000:
                    print("变道时间超过了5s仍符合条件，清空此次变道信息")
                    line_change[i] = []


def Iou(newMessage, oldMessage):
    if newMessage[0] <= oldMessage[0] <= newMessage[1] <= oldMessage[1]:
        return True
    if oldMessage[0] <= newMessage[0] <= oldMessage[1] <= newMessage[1]:
        return True
    if oldMessage[0] <= newMessage[0] <= newMessage[1] <= oldMessage[1]:
        return True
    if newMessage[0] < oldMessage[0] < oldMessage[1] <= newMessage[1]:
        return True
    if newMessage[1] <= oldMessage[1] <= newMessage[0] <= oldMessage[0]:
        return True
    if oldMessage[1] <= newMessage[1] <= oldMessage[0] <= newMessage[0]:
        return True
    if newMessage[1] <= oldMessage[1] <= oldMessage[0] <= newMessage[0]:
        return True
    if newMessage[1] <= oldMessage[1] <= oldMessage[0] <= newMessage[0]:
        return True
    return False


def Distance(a, b, threshold):
    return abs(a - b) < threshold if True else False


def isDuplicated(a, b, c1, c2):
    liCheng = []
    for i in range(len(b)):
        liCheng.append(b[i][cPotition])
    # print('licheng = ', liCheng, ", ceshi = ", a, ', c1= ', c1, ', c2 = ', c2)
    # 不允许攒相同的点
    if a not in liCheng and c1 == c2:
        return False
    # 允许攒相同的点
    # if a == b[-1][cPotition] and c1 == c2:
    #     return False
    elif a not in liCheng and c1 != c2:
        return True
    elif a in liCheng and c1 == c2:
        return True
    elif a in liCheng and c1 != c2:
        return True


def initialCars(car):
    global car_num
    global usedRecord
    global vt
    global entrance
    length = len(carStack)
    for messageNo in car:
        if len(messageNo) == 0:
            continue
        if messageNo[cPotition] in entrance and messageNo[cTongDao] != 0 and car_num < 8:
            print('开始检测车辆：', '通道=', messageNo[cTongDao], ',测区 = ', messageNo[cPotition])
            pushFlag = False
            for i in range(len(carStack) - 1, -1, -1):
                if messageNo not in usedRecord and isDuplicated(messageNo[cPotition], carStack[i], messageNo[cTongDao],
                                                                carStack[i][-1][cTongDao]):
                    usedRecord.append(messageNo)
                    continue
                if messageNo not in usedRecord and (
                        (Iou(messageNo[cScope], carStack[i][-1][cScope]) and not isDuplicated(messageNo[cPotition],
                                                                                              carStack[i],
                                                                                              messageNo[cTongDao],
                                                                                              carStack[i][-1][
                                                                                                  cTongDao]) and
                         messageNo[
                             cTongDao] == carStack[i][-1][cTongDao]
                         and messageNo[cPotition] - carStack[i][-1][cPotition] >= 0)
                        or
                        (Distance(messageNo[cPotition], carStack[i][-1][cPotition], threshold) and not isDuplicated(
                            messageNo[cPotition], carStack[i], messageNo[cTongDao], carStack[i][-1][cTongDao]) and
                         messageNo[cTongDao] == carStack[i][-1][
                             cTongDao] and messageNo[cPotition] -
                         carStack[i][-1][cPotition] >= 0)
                ):
                    if len(carStack[i]) >= initialNum:
                        carStack[i].append(messageNo)
                        vt = getSpeed(carStack[i])
                        # k.append(str(uuid.uuid1()))
                        k.append(car_num + 1)
                        temp = copy.deepcopy(messageNo)
                        ty = getCarType(carStack[i])
                        kType.append(ty)
                        line_change.append([])
                        push_v_predict.append(temp[_p])
                        road_change.append(0)
                        temp[cCartype] = ty
                        temp.append(vt)
                        car_his_pos.append([temp[_p]])
                        car_his_pos_time.append([temp[_t]])
                        v.append(temp)
                        carState.append(1)
                        vDeleteTime.append(time.time() * 1000)
                        is_single_cross.append(True)
                        pushFlag = True
                        car_num += 1
                        print("攒点删除:", carStack[i])
                        carStack.remove(carStack[i])
                        cStackDeleteTime.remove(cStackDeleteTime[i])
                        usedRecord.append(messageNo)
                    else:
                        carStack[i].append(messageNo)
                        pushFlag = True
                        usedRecord.append(messageNo)
            # 匹配失败则新建一条记录
            if not pushFlag and messageNo not in usedRecord:
                new = [messageNo]
                carStack.append(new)
                cStackDeleteTime.append(time.time() * 1000)
            usedRecord.append(messageNo)
    usedRecord = []


# 超时删除车
def deleteCars(_car):
    global k, car_num
    global v
    global carStack

    for i in range(len(foreCastAndBianDaoStack) - 1, -1, -1):
        # print("时间差2 = ", time.time() - ""cStackDeleteTime[i])
        if time.time() * 1000 - foreCastAndBianDaoStack[i][-1][cTime] > deleteZanDian:
            print('攒点超时删除', foreCastAndBianDaoStack[i])
            foreCastAndBianDaoStack.remove(foreCastAndBianDaoStack[i])

    for i in range(len(v) - 1, -1, -1):
        if chuKou < v[i][vScope][0]:
            v.remove(v[i])
            k.remove(k[i])
            carState.pop(i)
            kType.pop(i)
            line_change.remove(line_change[i])
            road_change.remove(road_change[i])
            vDeleteTime.pop(i)
            is_single_cross.pop(i)
            push_v_predict.remove(push_v_predict[i])
            car_his_pos_time.remove(car_his_pos_time[i])
            car_his_pos.remove(car_his_pos[i])
            # car_num = car_num - 1

    for i in range(len(carStack) - 1, -1, -1):
        # print("时间差2 = ", time.time() - ""cStackDeleteTime[i])
        if time.time() * 1000 - cStackDeleteTime[i] > stackTime:
            print('stack超时删除', carStack[i])
            carStack.remove(carStack[i])
            cStackDeleteTime.remove(cStackDeleteTime[i])


# 矩形匹配
def getMaxtrixLocation():
    global car
    maxtrixs = []
    channels = []
    for carInfor in car:
        if len(carInfor) == 0:
            continue
        # 通过大车记录矩形
        if carInfor[cCartype] == 1:
            maxtrixs.append(carInfor[cScope])
            # 记录大车所在通道
            channels.append(carInfor[cTongDao])
    print('maxtrix = ', maxtrixs)
    for i in range(len(car)):
        if len(car[i]) != 0:
            # 如果是大车则不需要判断
            if car[i][cCartype] == 1:
                continue
            for j in range(len(maxtrixs)):
                # 如果当前车辆影响范围在矩形内，并且这个车是小车或者伴随，则将这个记录抹除
                if isIn(car[i][cPotition], maxtrixs[j]) and car[i][cCartype] == 0 and abs(
                        car[i][cTongDao] - channels[j]) == 1:
                    print("排除：", car[i])
                    car[i] = []
                    break


# 返回车型
def getCarType(carInfor):
    global cCartype
    numZero = []
    numOne = []
    for infor in carInfor:
        if infor[cCartype] == 0:
            numZero.append(0)
        else:
            numOne.append(1)
    if len(numZero) >= len(numOne):
        return 0
    else:
        return 1


# 返回车辆影响范围
def getCarScope(carInfor):
    return carInfor[2]


# 返回车辆定位
def getCarLocation(carInfor):
    return carInfor[1]


# 判断小车是否在矩形范围内
def isIn(carPosition, scope):
    if scope[0] <= carPosition <= scope[1]:
        return True
    return False


# 计算平均速度d
def averageSpeed(speed):
    return np.average(speed)


# 计算测量速度(m/s)
def ceLiangSpeed(lastP, curP, lastTime, curTime):
    print('diff = ', (curTime - lastTime + 1) / 1000)
    a = (curTime - lastTime + 1) / 1000
    if a < 0:
        print('出错！！！！！！！！！！！！！！！！！！！！！')
    return (curP - lastP) / a


# 预测匹配函数(不赞点)
# def forecastDistance(zhiXing):
#     # 寻找全局变量
#     global car
#     global p
#     global vPosition
#     global vTime
#     global vSpeed
#     # 预测距离
#     forecastS = []
#     # 概率分布矩阵
#     forestcastArray = []
#     print('当前的car是：', car)
#     # 对每一辆历史记录的车计算一个预测距离
#     for i in range(len(k)):
#         # 上一次记录的时间
#         lastTime = vDeleteTime[i]
#         # 预测行驶距离 = 时间（需要将毫秒转成秒） * 速度
#         timeDiff = (time.time() * 1000 - lastTime) / 1000
#         if timeDiff > 0:
#             distance = timeDiff * abs(v[i][vSpeed])
#             # distance = ((time.time() * 1000 - lastTime) / 1000) * 22
#             forecastS.append(abs(distance))
#         else:
#             forecastS.append(0)
#     # 计算每一个历史记录的预测距离与当前所有定位的距离比值,如果有m个车在v中，car中有n条记录，那么将有m*n个记录
#     print('每辆车的预测距离：', forecastS)
#     for m in range(len(k)):
#         distribution = []
#         for n in range(len(car)):
#             if len(car[n]) == 0:
#                 distribution.append(0)
#                 continue
#             # 两者距离差值除预测距离
#             if forecastS[m] != 0 and v[m][vPosition] != car[n][cPotition]:
#                 # 历史记录与车的位置差值 / 预测距离
#                 xDistance = pow(abs(car[n][cTongDao] - v[m][vTongDao]) * 3.75, 2)
#                 yDistance = pow(abs(v[m][vPosition] - car[n][cPotition]), 2)
#                 trueDistance = pow(xDistance + yDistance, 1 / 2)
#                 temp1 = (trueDistance / abs(forecastS[m]))
#                 temp2 = (abs(forecastS[m]) / trueDistance)
#                 temp = min(temp1, temp2)
#                 # 存放到1的距离，越接近1表示可能性越大
#                 distribution.append(temp)
#             else:
#                 distribution.append(0)
#             # if forecastS[m] != 0 and v[m][vPosition] != car[n][cPotition]:
#             #     # 历史记录与车的位置差值 / 预测距离
#             #     temp1 = (abs(v[m][vPosition] - car[n][cPotition]) / abs(forecastS[m]))
#             #     temp2 = (abs(forecastS[m]) / abs(v[m][vPosition] - car[n][cPotition]))
#             #     temp = min(temp1, temp2)
#             #     # 存放到1的距离，越接近1表示可能性越大
#             #     distribution.append(temp)
#             # else:
#             #     distribution.append(0)
#         # 存放概率矩阵(形状是车的个数*当前定位个数)
#         forestcastArray.append(distribution)
#     # 遍历概率矩阵选出最合理的定位
#     maxK = []
#     maxV = []
#     # [概率， car索引]
#     yArray = []
#     print('预测行驶概率矩阵 = ', forestcastArray)
#     for m in range(len(v)):
#         # 找出每辆车最大概率的索引
#         maxIndex = np.argmax(forestcastArray[m])
#         # 保存这个概率值
#         maxK.append(forestcastArray[m][maxIndex])
#         # 保存这个概率对应的car索引
#         maxV.append(maxIndex)
#     # [概率，car索引]
#     for i in range(len(maxK)):
#         yArray.append([maxK[i], maxV[i]])
#     print('操作矩阵 = ', yArray)
#     # 去除定位点一样的概率更低的点
#     cleanData = getClean(yArray)
#     gaiLv = cleanData[1]
#     carIndex = cleanData[0]
#     # 存放筛选出的最有可能的车
#     vIndex = []
#     if len(gaiLv) == 0 or (len(gaiLv) == 0 and gaiLv[0] == 0):
#         return
#     for g in gaiLv:
#         vIndex.append(np.where(np.array(maxK) == g)[0])
#     for i in range(len(gaiLv)):
#         if len(vIndex[i]) > 1:
#             vNo = int(vIndex[i][0])
#         else:
#             vNo = int(vIndex[i])
#         carNo = carIndex[i]
#         lastSpeed = v[vNo][vSpeed]
#         if len(car[carNo]) == 0:
#             continue
#         realSpeed = ceLiangSpeed(v[vNo][vPosition], car[carNo][cPotition], v[vNo][vTime], car[carNo][cTime])
#         # newSpeed = (realSpeed + lastSpeed) / 2
#         print('第' + str(vNo) + '个车以概率' + str(gaiLv[i]) + '到达' + str(car[carNo]) + "他的速度为：", v[vNo][vSpeed])
#         if gaiLv[i] > zhiXing and realSpeed * lastSpeed >= 0 and v[vNo][vCartype] == car[carNo][cCartype] and abs(
#                 v[vNo][vTongDao] - car[carNo][cTongDao]) <= 1:
#             if v[vNo][_ch] != car[carNo][_ch]:
#                 count = 0
#                 for car_no in v:
#                     if car[carNo][_ch] == car_no[_ch] and (car[carNo][_p] - car_no[_p]) * (v[vNo][_p] - car_no[_p]) < 0:
#                         count += 1
#                 if count > 2:
#                     continue
#             print('预测匹配:', v[vNo], '匹配到', car[carNo], '概率为:', gaiLv[i], ' , 它的速度为：', v[vNo][vSpeed])
#             v[vNo][vPosition] = car[carNo][cPotition]
#             v[vNo][vScope] = car[carNo][cScope]
#             v[vNo][vCartype] = car[carNo][cCartype]
#             v[vNo][vTime] = car[carNo][cTime]
#             v[vNo][vTongDao] = car[carNo][cTongDao]
#             vDeleteTime[vNo] = time.time() * 1000
#             car[carNo] = []

# 攒点预测函数
def forecastDistance(zhiXing):
    car2 = []
    foreList = []
    # 加入攒够的轨迹
    for index in range(len(foreCastAndBianDaoStack)):
        if len(foreCastAndBianDaoStack[index]) == zanDianNeedNum + 1:
            car2.append(foreCastAndBianDaoStack[index][-1])
            foreList.append(index)
    # 预测距离
    forecastS = []
    # 概率分布矩阵
    forestcastArray = []

    if len(car2) > 0:
        print('当前的car是：', car2)
        # 对每一辆历史记录的车计算一个预测距离
        for i in range(len(k)):
            # 上一次记录的时间
            lastTime = vDeleteTime[i]
            # 预测行驶距离 = 时间（需要将毫秒转成秒） * 速度
            timeDiff = (time.time() * 1000 - lastTime) / 1000
            if timeDiff > 0:
                distance = timeDiff * abs(v[i][vSpeed])
                # distance = ((time.time() * 1000 - lastTime) / 1000) * 22
                forecastS.append(abs(distance))
            else:
                forecastS.append(0)
        # 计算每一个历史记录的预测距离与当前所有定位的距离比值,如果有m个车在v中，car中有n条记录，那么将有m*n个记录
        print('每辆车的预测距离：', forecastS)
        for m in range(len(k)):
            distribution = []
            for n in range(len(car2)):
                if len(car2[n]) == 0:
                    distribution.append(0)
                    continue
                # 两者距离差值除预测距离
                if forecastS[m] != 0 and v[m][vPosition] != car2[n][cPotition]:
                    # 历史记录与车的位置差值 / 预测距离
                    xDistance = pow(abs(car2[n][cTongDao] - v[m][vTongDao]) * 3.75, 2)
                    yDistance = pow(abs(v[m][vPosition] - car2[n][cPotition]), 2)
                    trueDistance = pow(xDistance + yDistance, 1 / 2)
                    temp1 = (trueDistance / abs(forecastS[m]))
                    temp2 = (abs(forecastS[m]) / trueDistance)
                    temp = min(temp1, temp2)
                    # 存放到1的距离，越接近1表示可能性越大
                    distribution.append(temp)
                else:
                    distribution.append(0)
            # 存放概率矩阵(形状是车的个数*当前定位个数)
            forestcastArray.append(distribution)
        # 遍历概率矩阵选出最合理的定位
        maxK = []
        maxV = []
        # [概率， car索引]
        yArray = []
        print('预测行驶概率矩阵 = ', forestcastArray)
        for m in range(len(v)):
            # 找出每辆车最大概率的索引
            maxIndex = np.argmax(forestcastArray[m])
            # 保存这个概率值
            maxK.append(forestcastArray[m][maxIndex])
            # 保存这个概率对应的car索引
            maxV.append(maxIndex)
        # [概率，car索引]
        for i in range(len(maxK)):
            yArray.append([maxK[i], maxV[i]])
        print('操作矩阵 = ', yArray)
        # 去除定位点一样的概率更低的点
        cleanData = getClean(yArray)
        gaiLv = cleanData[1]
        carIndex = cleanData[0]
        # 存放筛选出的最有可能的车
        vIndex = []
        if len(gaiLv) == 0 or (len(gaiLv) == 0 and gaiLv[0] == 0):
            return
        for g in gaiLv:
            vIndex.append(np.where(np.array(maxK) == g)[0])
        for i in range(len(gaiLv)):
            if len(vIndex[i]) > 1:
                vNo = int(vIndex[i][0])
            else:
                vNo = int(vIndex[i])
            carNo = carIndex[i]
            lastSpeed = v[vNo][vSpeed]

            if len(car2[carNo]) == 0:
                continue
            realSpeed = ceLiangSpeed(v[vNo][vPosition], car2[carNo][cPotition], v[vNo][vTime], car2[carNo][cTime])
            # newSpeed = (realSpeed + lastSpeed) / 2
            print('第' + str(vNo) + '个车以概率' + str(gaiLv[i]) + '到达' + str(car2[carNo]) + "他的速度为：", v[vNo][vSpeed])
            if gaiLv[i] > zhiXing and realSpeed * lastSpeed >= 0 and v[vNo][vCartype] == car2[carNo][cCartype] and abs(
                    v[vNo][vTongDao] - car2[carNo][cTongDao]) <= 1 and car2[carNo][cTime] - v[vNo][vTime] > 0:
                # if v[vNo][_ch] != car2[carNo][_ch]:
                #     count = 0
                #     for car_no in v:
                #         if car2[carNo][_ch] == car_no[_ch] and (car2[carNo][_p] - car_no[_p]) * (v[vNo][_p] - car_no[_p]) < 0:
                #             count += 1
                #     if count > 2:
                #         continue
                print('预测匹配:', v[vNo], '匹配到', car2[carNo], '概率为:', gaiLv[i], ' , 它的速度为：', v[vNo][vSpeed])
                print('lastSpeed = ', lastSpeed)
                print('reakSpeed = ', realSpeed)
                v[vNo][vPosition] = car2[carNo][cPotition]
                v[vNo][vScope] = car2[carNo][cScope]
                v[vNo][vCartype] = car2[carNo][cCartype]
                v[vNo][vTime] = car2[carNo][cTime]
                v[vNo][vTongDao] = car2[carNo][cTongDao]
                vDeleteTime[vNo] = time.time() * 1000
                foreCastAndBianDaoStack.remove(foreCastAndBianDaoStack[foreList[carNo]])


def getSpeed(carSta):
    # print('carsta = ', carSta)
    p1 = carSta[0][cPotition]
    direction = []
    # for j in range(len(carSta)):
    #     if j != 0:
    #         direction.append((carSta[j][cPotition] - p1) / abs((carSta[j][cPotition] - p1)))
    direction = np.array(direction)
    num1 = np.where(direction == 1)[0]
    num2 = np.where(direction == -1)[0]
    print(carSta[0][cTime])
    speed = abs(carSta[-1][cPotition] - p1) / ((carSta[-1][cTime] - carSta[0][cTime] + 1) / 1000)
    # print('时间差:', ((carSta[-1][cTime] - carSta[0][cTime])) if num1.sh)
    #     print('速度是：', speed)
    #     #ape[0] > num2.shape[0]:
    #     return speed
    # else:
    #     return -1 * speed
    if abs(speed) == 0:
        return 10
    else:
        return abs(speed)


# 攒点
def zanDian():
    print('hehe1')
    # 在最开始获取数组长度
    length = len(foreCastAndBianDaoStack)
    for c in car:
        pushFlag = False
        if len(c) > 0:
            if c[cPotition] != 0 and c[cPotition] not in entrance and c[cPotition] > entrance[-1]:
                for i in range(length):
                    # print('dd, ', foreCastAndBianDaoStack[i][-1][cPotition])
                    if 0 < c[cPotition] - foreCastAndBianDaoStack[i][-1][cPotition] < zanDianThreshold and c[
                        cTongDao] == foreCastAndBianDaoStack[i][-1][cTongDao] and len(
                        foreCastAndBianDaoStack[i]) <= zanDianNeedNum:
                        foreCastAndBianDaoStack[i].append(c)
                        pushFlag = True
            if not pushFlag:
                foreCastAndBianDaoStack.append([c])
    # print('foreCastAndBianDaoStack = ', foreCastAndBianDaoStack)


if __name__ == '__main__':
    encoder = RoadEncoder(lanes=4)
    msg = MessageServer()
    msg_s = MessagePublisher()
    msg_s.mile_range = encoder.mil_range
    t_r = threading.Thread(target=msg.ReceiveThread, args=())
    t = threading.Thread(target=msg_s.SendThread, args=())
    t.setDaemon(True)
    t_r.setDaemon(True)
    t_r.start()
    t.start()
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
    deleteZanDian = 1200
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
    # _max_time_limited = 0.2  # 0.5滑窗设为0.5  0.1设为0.1
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
    push_v_predict = []
    zhiXingDu = 0.85
    chuKou = 10708
    foreCastAndBianDaoStack = []
    push_tmp_vaild = []
    zanDianNeedNum = 1
    zanDianThreshold = 35
    carState = []  # 存放车辆行驶状态（0表示停车态、1表示行车态）
    flag = True
    is_single_cross = []

    while True:
        print()
        print('start:*****************************')
        time.sleep(_min_time_limited)
        data = msg.Dequeue()
        # if data is None:
        #     pass
        # else:
        #     map_data = encoder.MappingData(data)
        #     if map_data is None:
        #         pass
        #         # print('数据不全')
        #     else:
        #         print(map_data)

        if data is None:
            pass
        else:
            try:
                map_data = encoder.MappingData(data)
                if map_data is None:
                    pass
                    # print('数据不全')
                else:
                    print()
                    print("@@@@@@@@@@")
                    print('map_data:', map_data)
                    # file = open("E:\\推送信息6.txt", 'a+', encoding='UTF-8')
                    # file.writelines("第" + str(t) + "次：" + str(map_data) + "\n")
                    # file.close()
                    # for da in map_data:
                    #     channnelNo = da[0]
                    #     file = open("E:\\"+str(channnelNo)+"定位信息.txt", 'a+', encoding='utf-8')
                    #     file.writelines(str(da)+"\n")
                    #     file.close()
                    car = copy.deepcopy(map_data)
                    first_car = car[0]
                    if len(car) > 0:
                        pushT = car[0][-1]
                    # 矩形判断筛选
                    # getMaxtrixLocation()
                    tmp = []
                    for c in car:
                        if len(c) > 0:
                            if c[cTongDao] == 3 or c[cTongDao] == 2 or c[cTongDao] == 1:
                                tmp.append(c)
                    car = tmp
                    print('car = ', car)

                    for i in range(len(is_single_cross)):
                        is_single_cross[i] = True

                    # 影响范围判断
                    former_v = copy.deepcopy(v)
                    is_cross_match(k, v, car, kType)
                    is_path_judge(former_v, v)
                    # 匹配不上的点攒下来
                    zanDian()
                    # 预测匹配
                    forecastDistance(zhiXingDu)
                    # 推送时间
                    print('k = ', k)
                    print('v = ', v)
                    print('carStack = ', carStack)
                    print('stackLen = ', len(carStack))
                    print('car_num = ', car_num)
                    print('kType = ', kType)

                    # if len(v) == 4:
                    #     v.append([1, v[-1][vPosition], 0.3121134638786316, v[-1][vScope], 0, v[-1][vTime], v[-1][vSpeed]])
                    #     k.append(car_num + 1)
                    #     vDeleteTime.append(time.time() * 1000)
                    #     kType.append(0)
                    #     car_num += 1
                    #     car_his_pos.append([v[-1][_p]])
                    #     car_his_pos_time.append([v[-1][_t]])

                    # seven
                    # for i in range(len(v)):
                    #     if i < 2:
                    #         v[i][vCartype] = 1
                    #         kType[i] = 1
                    #     else:
                    #         v[i][vCartype] = 0
                    #         kType[i] = 0

                    if len(v) != len(vDeleteTime):
                        print("v出错！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！! !")
                    if len(cStackDeleteTime) != len(carStack):
                        print("stack出错！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！")
                    newV = copy.deepcopy(v)
                    tmp_v = copy.deepcopy(v)
                    # 车辆初始化

                    # if len(v) == 6:

                    # if len(newV) != 0 and len(k) != 0:
                    #     file = open("E:\\结果信息6.txt", 'a+', encoding='UTF-8')
                    #     file.writelines("第" + str(t) + "次：" + str(newV) + "\n")
                    #     file.closec

                    # # 多点平滑
                    # for i in range(len(newV)):
                    #     if tmp_v[i][_v] < 10:
                    #         carState[i] = 0
                    #         tmp_v[i][_v] = carState[i] * tmp_v[i][_v]
                    #     else:
                    #         carState[i] = 1
                    #     if len(former_v) != 0 and newV[i][_p] == former_v[i][_p]:
                    #         tmp_average_v = 0
                    #         for tmp_average_p in newV:
                    #             tmp_average_v += tmp_average_p[_v]
                    #         tmp_average_v = tmp_average_v / len(newV) if abs(tmp_average_v / len(newV)) > abs(
                    #             tmp_v[i][_v]) else tmp_v[i][_v]
                    #         push_v_predict[i] += int(tmp_average_v * 0.2)
                    #         tmp_v[i][_p] = int(push_v_predict[i])
                    #     else:
                    #         if abs(push_v_predict[i] - newV[i][_p]) > 30:
                    #             push_v_predict[i] = newV[i][_p]
                    #         else:
                    #             push_v_predict[i] = (push_v_predict[i] + newV[i][_p]) / 2

                    # 工况二
                    # if len(carState) > 2:
                    #     carState[-3] = 1

                    for i in range(len(newV)):
                        if tmp_v[i][_v] < 10 and tmp_v[i][_v] > 6:
                            carState[i] = 0
                            tmp_v[i][_v] = carState[i] * tmp_v[i][_v]
                        else:
                            carState[i] = 1

                        # two
                        # if len(carState) >= 4 and flag:
                        #     print('flag')
                        #     carState[3] = 0
                        #
                        #     flag = False

                        # if len(k) >= 4:
                        #     carState[k[3]] = 0
                        #     tmp_v[k - 1][_v] = carState[k - 1] * tmp_v[k - 1][_v]

                        if len(former_v) != 0 and newV[i] == former_v[i]:
                            tmp_average_v = 0
                            for tmp_average_p in newV:
                                tmp_average_v += tmp_average_p[_v]
                            tmp_average_v = tmp_average_v / len(newV) if abs(tmp_average_v / len(newV)) > abs(
                                tmp_v[i][_v]) else tmp_v[i][_v]
                            tmp_v[i][_p] = tmp_v[i][_p] + int(
                                tmp_v[i][_v] * ((time.time() * 1000 - vDeleteTime[i]) / 1000))

                    fake_tmp_v = []
                    tmp_k = copy.deepcopy(k)
                    fake_k = []
                    for i in range(len(newV)):
                        newV[i][-2] = pushT
                        if tmp_v[i][_p] > chuKou:
                            print('i =  ', i, ', p = ', tmp_v[i][_p])
                            fake_tmp_v.append(tmp_v[i])
                            fake_k.append(k[i])

                    for i in range(len(fake_tmp_v)):
                        tmp_v.remove(fake_tmp_v[i])
                        tmp_k.remove(fake_k[i])

                    print("%%", tmp_v, tmp_k)
                    if len(newV) != 0 and len(k) != 0:
                        print('vv = ', newV)
                        # print("推送的v为", tmp_v)
                        # msg_s.PackBag(newV[0][-2], k, newV)
                        msg_s.PackBag(newV[0][-2], tmp_k, tmp_v)
                        print("推送成功！")

                    push_tmp_vaild = copy.deepcopy(tmp_v)
                    # for i in range(len(newV)):
                    #     newV[i][-2] = pushT
                    # if len(newV) != 0 and len(k) != 0:
                    #     print('vv = ', newV)
                    #     print("push_v_predict", push_v_predict)
                    #     # print("推送的v为", tmp_v)
                    #     # msg_s.PackBag(newV[0][-2], k, newV)
                    #     msg_s.PackBag(newV[0][-2], k, tmp_v)

                    # 车辆初始化
                    initialCars(car)
                    # 车辆超时删除
                    deleteCars(first_car)
                    print('end:*****************************')
                    print()
            except Exception as e:
                print(e)
