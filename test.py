import numpy as np




# def forecastDistance():
#     # 寻找全局变量
#     global car
#     global v
#     global p
#     global vPosition
#     global vTime
#     global vSpeed
#
#     # 预测距离
#     forecastS = []
#     # 概率分布矩阵
#     forestcastArray = []
#     # 对每一辆历史记录的车计算一个预测距离
#     for i in range(len(v)):
#         # 上一次记录的时间
#         lastTime = vDeleteTime[i]
#         # 预测行驶距离 = 时间（需要将毫秒转成秒） * 速度
#         distance = ((time.time() - lastTime) / 1000) * v[i][vSpeed]
#         forecastS.append(abs(distance))
#     # 计算每一个历史记录的预测距离与当前所有定位的距离比值,如果有m个车在v中，car中有n条记录，那么将有m*n个记录
#     for m in range(len(v)):
#         distribution = []
#         for n in range(len(car)):
#             if len(car[n]) == 0:
#                 continue
#             # 两者距离差值比上预测距离
#             temp = (abs(v[m][vPosition] - car[n][p]) / forecastS[m])
#             # 存放到1的距离，越接近1表示可能性越大
#             distribution.append(abs(1 - temp))
#         # 存放概率矩阵(形状是车的个数*当前定位个数)
#         forestcastArray.append(distribution)
#     # 遍历概率矩阵选出最合理的定位
#     minK = []
#     minV = []
#     for m in range(len(v)):
#         # 找出每辆车最接近1的索引
#         minIndex = np.argmin(forestcastArray[m])
#         # 保存这个概率值
#         minK.append(forestcastArray[m][minIndex])
#         # 保存这个概率对应的car索引
#         minV.append(minIndex)
#     # 找出所有车里面可能性最大的一个
#     result = np.min(minK)
#     # 找出可能性最大的一个v对应的索引
#     vNo = np.argmin(minK)
#     # 找出car对应的索引
#     carNo = minV[vNo]
#     # 如果这个比值在0.7与1.3之间
#     if 0.8 < result < 1.2:
#         # 计算测量速度
#         lastSpeed = v[vNo][vSpeed]
#         if abs(v[vNo][vTime] - car[carNo][cTime]) > 0.05:
#             realSpeed = ceLiangSpeed(v[vNo][vPosition], car[carNo][p], v[vNo][vTime], car[carNo][cTime])
#             newSpeed = (realSpeed + lastSpeed) / 2
#             v[vNo][vSpeed] = newSpeed
#             # 更新v与car，并且推送
#             v[vNo][vPosition] = car[carNo][cPotition]
#             v[vNo][vScope] = car[carNo][cScope]
#             v[vNo][vCartype] = car[carNo][cCartype]
#             v[vNo][vTime] = car[carNo][cTime]
#             v[vNo][vTongDao] = car[carNo][cTongDao]
#             print("当前推送的是", v[vNo])
#             car[carNo] = []
#             print("当前预测了")

def is_cross_match(record_k, record_v, info_car):
    def judge_condition_cross(x, y):
        flag = False
        if len(x) == 0:
            return False
        if x[_car_type] == y[_car_type] and 1000 * _max_time_limited * 20 > x[_t] - y[
            _t] >= _min_time_limited * 1000  and (
                x[_scope][0] <= y[_scope][1] <=
                x[_scope][1] or x[_scope][0] <=
                y[_scope][0] <=
                x[_scope][1] or y[_scope][0] <= x[_scope][1] <=
                y[_scope][1]):
            flag = True  # 判断预测条件
        return flag

    # 匹配同车道
    for i in range(len(info_car)):
        for j in range(len(record_v)):
            if judge_condition_cross(info_car[i], record_v[j]) and record_v[j][_ch] == info_car[i][_ch]:
                if  ((info_car[i][_p] - record_v[j][_p]) / (info_car[i][_t] - record_v[j][_t])) * record_v[j][_v] >= 0:
                    if info_car[i][_p] == record_v[j][_p]:
                        car_speed = record_v[j][_v]
                    else:
                        car_speed = ((info_car[i][_p] - record_v[j][_p]) * 1000 / (
                                info_car[i][_t] - record_v[j][_t]) + record_v[j][_v]) / 2
                    info_car[i].append(car_speed)  # 加入速度
                    print("交叉匹配同车道" + "车辆" + str(record_k[j]) + "位置从" + str(record_v[j][_p]) + '变为' + str(
                        info_car[i][_p]), info_car[i])
                    record_v[j] = info_car[i]
                else:
                    print("交叉匹配同车道出现位置倒退，只更新时间")
                    record_v[j][_t] = info_car[i][_t]
                # vDeleteTime[j] = time.time() * 1000
                info_car[i] = []
                break

    # 匹配不同车道
    for i in range(len(info_car)):
        for j in range(len(record_v)):
            if judge_condition_cross(info_car[i], record_v[j]) and abs(
                    record_v[j][_ch] - info_car[i][_ch]) == 1:  # 默认只会变一个道
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
                else:
                    print("交叉匹配相邻车道出现位置倒退，只更新时间")
                    record_v[j][_t] = info_car[i][_t]
                # vDeleteTime[j] = time.time() * 1000
                info_car[i] = []
                break
    return record_k, record_v, info_car
def is_smalldistance(record_k, record_v, info_car):
    def judge_condition_small(x, y):
        if len(x) == 0:
            return False
        if x[_car_type] == y[_car_type] and 1000 * _max_time_limited * 20 > x[_t] - y[
            _t] >= _min_time_limited * 1000 and ((x[_p] - y[_p]) / (x[_t] - y[_t])) * y[_v] >= 0:
            # 判断预测条件
            return True

    # 同个车道匹配

    for i in range(len(info_car)):
        small_distance = 30
        small_index = -1
        for j in range(len(record_v)):
            if judge_condition_small(info_car[i], record_v[j]) and record_v[j][_ch] == info_car[i][_ch]:
                if abs(info_car[i][_p] - record_v[j][_p]) < small_distance * ((
                        info_car[i][_t] - record_v[j][_t] + 1000) // 1000):
                    print(small_distance * ((info_car[i][_t] - record_v[j][_t] + 1000) // 1000))
                    small_distance = abs(info_car[i][_p] - record_v[j][_p])
                    small_index = j
        if small_index != -1:
            car_speed = ((info_car[i][_p] - record_v[small_index][_p]) * 1000 / (
                    info_car[i][_t] - record_v[small_index][_t]) + record_v[small_index][_v]) / 2
            info_car[i].append(car_speed)  # 加入速度
            print("相邻匹配同车道" + "车辆" + str(record_k[small_index]) + "位置从" + str(record_v[small_index][_p]) + '变为' + str(
                info_car[i][_p]), info_car[i])
            record_v[small_index] = info_car[i]
            # vDeleteTime[small_index] = time.time() * 1000
            info_car[i] = []

    for i in range(len(info_car)):
        small_distance = 40
        small_index = -1
        for j in range(len(record_v)):
            if judge_condition_small(info_car[i], record_v[j]) and abs(
                    record_v[j][_ch] - info_car[i][_ch]) == 1:
                if abs(info_car[i][_p] - record_v[j][_p]) < small_distance:
                    small_distance = abs(info_car[i][_p] - record_v[j][_p])
                    small_index = j
        if small_index != -1:
            car_speed = ((info_car[i][_p] - record_v[small_index][_p]) * 1000 / (
                    info_car[i][_t] - record_v[small_index][_t]) + record_v[small_index][_v]) / 2
            info_car[i].append(car_speed)  # 加入速度
            record_v[small_index] = info_car[i]
            # vDeleteTime[small_index] = time.time() * 1000
            print("交叉匹配相邻车道" + '通道' + str(record_v[small_index][_ch]) + "变为" + str(info_car[i][_ch]),
                  "车辆" + str(record_k[small_index]) + "位置从" + str(record_v[small_index][_p]) + '变为' + str(
                      info_car[i][_p]),
                  info_car[i])
            info_car[i] = []


if __name__ == '__main__':
    print(55 / 1000)
    _ch = 0  # 通道号
    _p = 1  # 位置
    _scope = 3  # 范围
    _t = 5  # 时间
    _car_type = 4
    _v = 6
    _max_time_limited = 0.5  # 0.5滑窗设为0.5  0.1设为0.1
    _min_time_limited = 0.05
    k = ['96bb2462-ae5e-11ec-aa22-484d7eb4b3e5']
    v = [[3, 10431, 2.87746524810791, [10396, 10446], 0, 1648458363210, 10.964912280701753]]
    map_data= [[3, 10492, 0.697441816329956, [10486, 10492], 0, 1648458364208, 54.0493351212426]]
    is_cross_match(k,v,map_data)
    is_smalldistance(k,v,map_data)


