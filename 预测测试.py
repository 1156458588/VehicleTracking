import numpy as np
import time

from match import getClean, ceLiangSpeed

def zanDian():
    # 在最开始获取数组长度
    length = len(foreCastAndBianDaoStack)
    for c in car:
        pushFlag = False
        if len(c) > 0 and c[cPotition] != 0 and c[cPotition] not in entrance:
            for i in range(length):
                if 0 < c[cPotition] - foreCastAndBianDaoStack[i][-1][cPotition] < zanDianThreshold and c[cTongDao] == foreCastAndBianDaoStack[i][-1][cTongDao] and len(foreCastAndBianDaoStack[i]) <= zanDianNeedNum:
                    foreCastAndBianDaoStack[i].append(c)
                    pushFlag = True
            if not pushFlag:
                foreCastAndBianDaoStack.append([c])
    print('foreCastAndBianDaoStack = ', foreCastAndBianDaoStack)


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
    print('当前的car是：', car2)
    if len(car2) > 0:
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
                    v[vNo][vTongDao] - car2[carNo][cTongDao]) <= 1:
                # if v[vNo][_ch] != car2[carNo][_ch]:
                #     count = 0
                #     for car_no in v:
                #         if car2[carNo][_ch] == car_no[_ch] and (car2[carNo][_p] - car_no[_p]) * (v[vNo][_p] - car_no[_p]) < 0:
                #             count += 1
                #     if count > 2:
                #         continue
                print('预测匹配:', v[vNo], '匹配到', car2[carNo], '概率为:', gaiLv[i], ' , 它的速度为：', v[vNo][vSpeed])
                v[vNo][vPosition] = car2[carNo][cPotition]
                v[vNo][vScope] = car2[carNo][cScope]
                v[vNo][vCartype] = car2[carNo][cCartype]
                v[vNo][vTime] = car2[carNo][cTime]
                v[vNo][vTongDao] = car2[carNo][cTongDao]
                vDeleteTime[vNo] = time.time() * 1000
                foreCastAndBianDaoStack.remove(foreCastAndBianDaoStack[foreList[carNo]])
    else:
        print('asd')


if __name__ == '__main__':
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
    # 删除车辆时间
    timeThreshold = 2000
    # 栈时间
    stackTime = 1000

    kType = []
    _ch = 0  # 通道号
    _p = 1  # 位置
    _max = 2
    _scope = 3  # 范围
    _t = 5  # 时间
    _car_type = 4
    _v = 6
    _max_time_limited = 0.2  # 0.5滑窗设为0.5  0.1设为0.1
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

    cStackDeleteTime = []
    t = 0
    # 车辆入口
    start = 10048
    end = 9998
    entrance = [i for i in range(end, start)]

    car_his_pos = []
    car_his_pos_time = []
    zhiXingDu = 0.9
    chuKou = 10698
    foreCastAndBianDaoStack = []
    zanDianNeedNum = 1
    zanDianThreshold = 35
    vDeleteTime = [time.time() * 1000 - 2000, time.time() * 1000 - 2000]
    k = [1, 2]
    v = [[3, 10715, 48.64324188232422, [10728, 10743], 0, 1649647322407, 15], [0, 10715, 48.64324188232422, [10728, 10743], 0, 1649647322407, 15]]

    car = [[3, 10738, 48.64324188232422, [10728, 10743], 0, 1649647322407]]
    zanDian()
    car = [[]]
    zanDian()
    forecastDistance(zhiXingDu)
    print('f = ', foreCastAndBianDaoStack)