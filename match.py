# info_car [[ch,p,scope,t, maxValue, carType]]
# -record_v = [[ch, p,scope,t,v]]
# scope = [min,max]
import sys
import threading
import time
import uuid
import copy

import numpy as np
import pandas as pd
import random
from ZMQServer import MessageServer
from ZMQClient import MessageClient
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
            maxV.append(value[0])
            maxK.append(value[1])
    return maxK, maxV


def is_cross_match(record_k, record_v, info_car):
    def judge_condition_cross(x, y):
        flag = False
        if len(x) == 0:
            return False
        if 1000 * _max_time_limited * 20 > x[_t] - y[
            _t] >= _min_time_limited * 1000 and (
                x[_scope][0] <= y[_scope][1] <=
                x[_scope][1] or x[_scope][0] <=
                y[_scope][0] <=
                x[_scope][1] or y[_scope][0] <= x[_scope][1] <=
                y[_scope][1]):
            flag = True  # 判断预测条件
        return flag


    def judge_condition_small(x, y):
        if len(x) == 0:
            return False
        if  1000 * _max_time_limited * 20 > x[_t] - y[
            _t] >= _min_time_limited * 1000 and ((x[_p] - y[_p]) / (x[_t] - y[_t])) * y[_v] >= 0:
            # 判断预测条件
            return True

    # 同个车道匹配

    # 匹配同车道
    for i in range(len(info_car)):
        for j in range(len(record_v)):
            if judge_condition_cross(info_car[i], record_v[j]) and record_v[j][_ch] == info_car[i][_ch] and record_v[j][_p] > start+25:
                if ((info_car[i][_p] - record_v[j][_p]) / (info_car[i][_t] - record_v[j][_t])) * record_v[j][_v] >= 0:
                    if info_car[i][_p] - record_v[j][_p]!=0:
                        if len(historySpeeds[j])>4:
                            car_speed = (np.sum(historySpeeds[j][-1:-5])+(info_car[i][_p] - record_v[j][_p]) * 1000 / (
                                    info_car[i][_t] - record_v[j][_t])) / 5
                        else:
                            car_speed = (np.sum(historySpeeds[j])+(info_car[i][_p] - record_v[j][_p]) * 1000 / (
                                    info_car[i][_t] - record_v[j][_t]))/(len(historySpeeds[j])+1)
                        info_car[i].append(car_speed)  # 加入速度
                        print("交叉匹配同车道" + "车辆" + str(record_k[j]) + "位置从" + str(record_v[j][_p]) + '变为' + str(
                            info_car[i][_p]), info_car[i])
                        record_v[j] = info_car[i]
                        vDeleteTime[j] = time.time() * 1000
                    info_car[i] = []
                else:
                    print("交叉匹配同车道出现位置倒退，只更新时间", record_v[j], info_car[i])
                    record_v[j][_t] = info_car[i][_t]
                    vDeleteTime[j] = time.time() * 1000
                    info_car[i] = []
                break

    for i in range(len(info_car)):
        small_distance = 30
        small_index = -1
        for j in range(len(record_v)):
            if judge_condition_small(info_car[i], record_v[j]) and record_v[j][_ch] == info_car[i][_ch]:
                if abs(info_car[i][_p] - record_v[j][_p]) < small_distance * ((
                        info_car[i][_t] - record_v[j][_t] + 1000) // 1000):
                    small_distance = abs(info_car[i][_p] - record_v[j][_p])
                    small_index = j
        if small_index != -1:
            car_speed = ((info_car[i][_p] - record_v[small_index][_p]) * 1000 / (
                    info_car[i][_t] - record_v[small_index][_t]) + record_v[small_index][_v]) / 2
            info_car[i].append(car_speed)  # 加入速度
            print("相邻匹配同车道" + "车辆" + str(record_k[small_index]) + "位置从" + str(record_v[small_index][_p]) + '变为' + str(
                info_car[i][_p]), info_car[i])
            record_v[small_index] = info_car[i]
            vDeleteTime[small_index] = time.time() * 1000
            info_car[i] = []

    # 匹配不同车道
    for i in range(len(info_car)):
        for j in range(len(record_v)):
            if judge_condition_cross(info_car[i], record_v[j]) and abs(
                    record_v[j][_ch] - info_car[i][_ch]) == 1 and record_v[j][_p] > (start + 25):  # 默认只会变一个道
                if ((info_car[i][_p] - record_v[j][_p]) / (info_car[i][_t] - record_v[j][_t])) * record_v[j][_v] >= 0:
                    if info_car[i][_p] == record_v[j][_p]:
                        car_speed = record_v[j][_v]
                    else:
                        car_speed = ((info_car[i][_p] - record_v[j][_p]) * 1000 / (
                                info_car[i][_t] - record_v[j][_t]) + record_v[j][_v]) / 2
                    info_car[i].append(car_speed)  # 加入速度
                    print("交叉匹配相邻车道" + '通道' + str(record_v[j][_ch]) + "变为" + str(info_car[i][_ch]),
                          "车辆" + str(record_k[j]) + "位置从" + str(record_v[j][_p]) + '变为' + str(info_car[i][_p]),
                          info_car[i])
                    record_v[j] = info_car[i]
                    vDeleteTime[j] = time.time() * 1000
                    info_car[i] = []
                break
    return record_k, record_v, info_car


# 基于车辆最短距离
# def is_smalldistance(record_k, record_v, info_car):

    # for i in range(len(info_car)):
    #     small_distance = 40
    #     small_index = -1
    #     for j in range(len(record_v)):
    #         if judge_condition_small(info_car[i], record_v[j]) and abs(
    #                 record_v[j][_ch] - info_car[i][_ch]) == 1:
    #             if abs(info_car[i][_p] - record_v[j][_p]) < small_distance:
    #                 small_distance = abs(info_car[i][_p] - record_v[j][_p])
    #                 small_index = j
    #     if small_index != -1:
    #         car_speed = ((info_car[i][_p] - record_v[small_index][_p]) * 1000 / (
    #                 info_car[i][_t] - record_v[small_index][_t]) + record_v[small_index][_v]) / 2
    #         info_car[i].append(car_speed)  # 加入速度
    #         record_v[small_index] = info_car[i]
    #         vDeleteTime[small_index] = time.time() * 1000
    #         print("相邻匹配相邻车道" + '通道' + str(record_v[small_index][_ch]) + "变为" + str(info_car[i][_ch]),
    #               "车辆" + str(record_k[small_index]) + "位置从" + str(record_v[small_index][_p]) + '变为' + str(
    #                   info_car[i][_p]),
    #               info_car[i])
    #         info_car[i] = []


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
    if a not in liCheng and c1 == c2:
        return False
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
    for messageNo in car:
        if len(messageNo) == 0:
            continue
        if messageNo[cPotition] in entrance and messageNo[cTongDao] != 0:
            pushFlag = False
            for i in range(len(carStack) - 1, -1, -1):
                if messageNo not in usedRecord and isDuplicated(messageNo[cPotition], carStack[i], messageNo[cTongDao], carStack[i][-1][cTongDao]):
                    usedRecord.append(messageNo)
                    continue
                if messageNo not in usedRecord and (
                        (Iou(messageNo[cScope], carStack[i][-1][cScope]) and not isDuplicated(messageNo[cPotition],
                                                                                              carStack[i], messageNo[cTongDao], carStack[i][-1][cTongDao]) and messageNo[
                             cTongDao] == carStack[i][-1][cTongDao]
                            and messageNo[cPotition] - carStack[i][-1][cPotition] > 0)
                        # or
                        # (Distance(messageNo[cPotition], carStack[i][-1][cPotition], threshold) and not isDuplicated(
                        #     messageNo[cPotition], carStack[i]) and messageNo[cTongDao] == carStack[i][-1][
                        # cTongDao] and messageNo[cCartype] == carStack[i][-1][cCartype])
                ) :
                    if len(carStack[i]) >= initialNum:
                        vt = getSpeed(carStack[i])
                        k.append(str(uuid.uuid1()))
                        temp = messageNo
                        temp.append(vt)
                        historySpeeds.append([vt])
                        v.append(temp)
                        vDeleteTime.append(time.time() * 1000)
                        pushFlag = True
                        car_num += 1
                        print("删除:", carStack[i])
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

    # deleteTime = time.time() * 1000
    # 倒叙遍历
    # for i in range(len(v) - 1, -1, -1):
    #     print("v时间差1 = ", time.time() * 1000, ",v时间2 = ", vDeleteTime[i])
    #     if time.time() * 1000 - vDeleteTime[i] > timeThreshold:
    #         print("v删除：", v[i])
    #         v.remove(v[i])
    #         k.remove(k[i])
    #         vDeleteTime.remove(vDeleteTime[i])
    #         car_num = car_num - 1

    for i in range(len(carStack) - 1, -1, -1):
        # print("时间差2 = ", time.time() - ""cStackDeleteTime[i])
        if time.time() * 1000 - cStackDeleteTime[i] > stackTime:
            print('stack删除', carStack[i])
            carStack.remove(carStack[i])
            cStackDeleteTime.remove(cStackDeleteTime[i])


# 矩形匹配
def getMaxtrixLocation():
    global car
    maxtrixs = []
    for carInfor in car:
        if len(carInfor) == 0:
            continue
        # 通过大车记录矩形
        if carInfor[cCartype] == 1:
            maxtrixs.append(carInfor[cScope])
    print('maxtrix = ', maxtrixs)
    for i in range(len(car)):
        if len(car[i]) != 0:
            # 如果是大车则不需要判断
            if car[i][cCartype] == 1:
                continue
            for juXing in maxtrixs:
                # 如果当前车辆影响范围在矩形内，并且这个车是小车或者伴随，则将这个记录抹除
                if isIn(car[i][cPotition], juXing) and car[i][cCartype] == 0:
                    print("排除：", car[i])
                    car[i] = []
                    break
# 返回车型
def getCarType(carInfor):
    if carInfor[-1] == 1:
        return 1  # 大车
    else:
        return 0  # 小车


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
    return (curP - lastP) / ((curTime - lastTime) / 1000)


def forecastDistance():
    # 寻找全局变量
    global car
    global v
    global p
    global vPosition
    global vTime
    global vSpeed
    # 预测距离
    forecastS = []
    # 概率分布矩阵
    forestcastArray = []
    # 对每一辆历史记录的车计算一个预测距离
    for i in range(len(v)):
        # 上一次记录的时间
        lastTime = vDeleteTime[i]
        # 预测行驶距离 = 时间（需要将毫秒转成秒） * 速度
        print((time.time() * 1000 - lastTime) / 1000)
        distance = ((time.time() * 1000 - lastTime) / 1000) * v[i][vSpeed]
        forecastS.append(abs(distance))
    # 计算每一个历史记录的预测距离与当前所有定位的距离比值,如果有m个车在v中，car中有n条记录，那么将有m*n个记录
    print('预测距离：', forecastS)
    for m in range(len(v)):
        distribution = []
        for n in range(len(car)):
            if len(car[n]) == 0:
                continue
            # 两者距离差值除预测距离
            temp1 = (abs(v[m][vPosition] - car[n][cPotition]) / abs(forecastS[m]))
            temp2 = (abs(forecastS[m]) / abs(v[m][vPosition] - car[n][cPotition]))
            temp = min(temp1, temp2)
            # 存放到1的距离，越接近1表示可能性越大
            distribution.append(temp)
        # 存放概率矩阵(形状是车的个数*当前定位个数)
        forestcastArray.append(distribution)
    # 遍历概率矩阵选出最合理的定位
    maxK = []
    maxV = []
    # 概率， car索引
    yArray = []
    print('forestcastArray = ', forestcastArray)
    for m in range(len(v)):
        # 找出每辆车最大概率的索引
        minIndex = np.argmax(forestcastArray[m])
        # 保存这个概率值
        maxK.append(forestcastArray[m][minIndex])
        # 保存这个概率对应的car索引
        maxV.append(minIndex)
    for i in range(len(maxK)):
        yArray.append([maxK[i], maxV[i]])
    print('yA = ', yArray)
    cleanData = getClean(yArray)
    print('maxK = ', maxK)
    print('maxV = ', maxV)
    gaiLv = cleanData[1]
    carIndex = cleanData[0]
    vIndex = []
    print('gailv = ', gaiLv)
    print('carIndex = ', carIndex)
    for g in gaiLv:
        vIndex.append(np.where(np.array(maxK) == g)[0])
    print('vindex=', vIndex)
    for i in range(len(gaiLv)):
        vNo = int(vIndex[i])
        carNo = carIndex[i]
        lastSpeed = v[vNo][vSpeed]
        realSpeed = ceLiangSpeed(v[vNo][vPosition], car[carNo][cPotition], v[vNo][vTime], car[carNo][cTime])
        newSpeed = (realSpeed + lastSpeed) / 2
        print(realSpeed)
        if gaiLv[i] > 0.83 and realSpeed * lastSpeed >= 0:
            print('预测匹配:', v[vNo], '匹配到', car[carNo], '置信度为:', gaiLv[i])
            v[vNo][vSpeed] = newSpeed
            v[vNo][vPosition] = car[carNo][cPotition]
            v[vNo][vScope] = car[carNo][cScope]
            v[vNo][vCartype] = car[carNo][cCartype]
            v[vNo][vTime] = car[carNo][cTime]
            v[vNo][vTongDao] = car[carNo][cTongDao]
            car[carNo] = []


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
    print('1 = ', str(carSta[-1][cTime]))
    print('dd = ', str(carSta[-1][cTime] - carSta[0][cTime]))
    print(carSta[0][cTime])
    speed = abs(carSta[-1][cPotition] - p1) / ((carSta[-1][cTime] - carSta[0][cTime] + 1) / 1000)
    print('位置差：', abs(carSta[-1][cPotition] - p1))
    # print('时间差:', ((carSta[-1][cTime] - carSta[0][cTime])) if num1.sh)
    #     print('速度是：', speed)
    #     #ape[0] > num2.shape[0]:
    #     return speed
    # else:
    #     return -1 * speed
    return abs(speed)


def is_path_judge(former_record_v, new_record_v):
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
                        _p]:
                        tmp = new_record_v[j]
                        car_speed_i = ((new_record_v[j][_p] - former_record_v[i][_p]) * 1000 / (
                                new_record_v[j][_t] - former_record_v[i][_t]) + former_record_v[i][_v]) / 2
                        car_speed_j = ((new_record_v[i][_p] - former_record_v[j][_p]) * 1000 / (
                                new_record_v[i][_t] - former_record_v[j][_t]) + former_record_v[j][_v]) / 2
                        new_record_v[j] = new_record_v[i]
                        new_record_v[i] = tmp
                        new_record_v[i][-1] = car_speed_i
                        new_record_v[j][-1] = car_speed_j
                        print("位置匹配错误，已更改", tmp, "改为", new_record_v[j])

if __name__ == '__main__':
    encoder = RoadEncoder(lanes=4)
    msg = MessageServer()
    msg_s = MessageClient(ip='127.0.0.1')
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
    initialNum = 2
    # 定位索引
    p = 1
    # 范围索引
    s = 2
    # 时间索引
    timeIndex = -2
    # 删除车辆时间
    timeThreshold = 2000
    # 栈时间
    stackTime = 800
    # 初始化速度
    vt = 70
    k = []
    v = []
    _ch = 0  # 通道号
    _p = 1  # 位置
    _scope = 3  # 范围
    _t = 5  # 时间
    _car_type = 4
    _v = 6
    _max_time_limited = 0.1  # 0.5滑窗设为0.5  0.1设为0.1
    _min_time_limited = 0.01  # 0.5滑窗设为0.3  0.1设为0.05
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
    start = 10043
    entrance = [i for i in range(9998, start)]
    historySpeeds = []

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
                    # print('map_data:', map_data)
                    # file = open("E:\\推送信息6.txt", 'a+', encoding='UTF-8')
                    # file.writelines("第" + str(t) + "次：" + str(map_data) + "\n")
                    # file.close()
                    car = copy.deepcopy(map_data)
                    first_car = car[0]
                    if len(car) > 0:
                        pushT = car[0][-1]
                    # 矩形判断筛选
                    getMaxtrixLocation()
                    # print('asd')
                    tmp = []

                    for c in car:
                        if len(c) > 0:
                            if c[cTongDao] == 2 or c[cTongDao] == 1 or c[cTongDao] == 0 or c[cTongDao] == 3:
                                tmp.append(c)

                    car = tmp
                    print('car = ', car)
                    # 影响范围判断
                    former_v = copy.deepcopy(v)
                    is_cross_match(k, v, car)

                    # is_smalldistance(k, v, car)
                    is_path_judge(former_v, v)
                    # 车辆初始化
                    initialCars(car)
                    # 预测匹配
                    # forecastDistance()
                    # 车辆超时删除
                    deleteCars(first_car)



                    # 推送时间
                    print('k = ', k)
                    print('v = ', v)
                    print('carStack = ', carStack)
                    print('stackLen = ', len(carStack))
                    print('car_num = ', car_num)
                    if len(v) != len(vDeleteTime):
                        print("v出错！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！1")
                    car = []
                    if len(cStackDeleteTime) != len(carStack):
                        print("stack出错！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！")

                    newV = copy.deepcopy(v)

                    # if len(newV) != 0 and len(k) != 0:
                    #     file = open("E:\\结果信息6.txt", 'a+', encoding='UTF-8')
                    #     file.writelines("第" + str(t) + "次：" + str(newV) + "\n")
                    #     file.close()


                    for i in range(len(newV)):
                        newV[i][-2] = pushT

                    if len(newV) != 0 and len(k) != 0:
                        print('vv = ', newV)
                        tmp_v = []
                        tmp_k = []
                        for i in range(len(former_v)):
                            if former_v[i]!=newV[i]:
                                tmp_v.append(newV[i])
                                tmp_k.append(k[i])
                        msg_s.PackBag(newV[0][-2], tmp_k, tmp_v)
                        # print("推送成功！")
                    t = t + 1
                    print('end:*****************************')
                    print()
            except Exception as e:
                print(e)
