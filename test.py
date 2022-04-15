import copy

import scipy,scipy.optimize
import  numpy as np



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
        if y[_car_type]==0 and (
                x[_scope][0] <= y[_scope][1] <=
                x[_scope][1] or x[_scope][0] <=
                y[_scope][0] < x[_scope][1] or y[_scope][0] < x[_scope][1] <= y[_scope][1]):
            return False

        if 1000 * _max_time_limited * 20 > x[_t] - y[_t] >= _min_time_limited * 1000 and (
                (x[_p] - y[_p]) / (x[_t] - y[_t])) * y[_v] > 0:
            # 判断预测条件
            return True

    # 去点大车旁边车道的定位点
    # for i in range(len(k_type)):
    #     if k_type[i] == 1:
    #         for j in range(len(info_car)):
    #             if judge_condition_cross(info_car[j], record_v[i]) and abs(info_car[j][_ch] - record_v[i][_ch])==1:
    #                 info_car[j] = []

    # 匹配同车道
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
    # 匹配不同车道
    # for i in range(len(info_car)):
    #     for j in range(len(record_v)):
    #         if judge_condition_cross(info_car[i], record_v[j]) and abs(
    #                 record_v[j][_ch] - info_car[i][_ch]) == 1 and record_v[j][_p] > (start):  # 默认只会变一个道
    #             if ((info_car[i][_p] - record_v[j][_p]) / (info_car[i][_t] - record_v[j][_t])) * record_v[j][_v] >= 0:
    #                 print("交叉匹配相邻车道" + '通道' + str(record_v[j][_ch]) + "变为" + str(info_car[i][_ch]),
    #                       "车辆" + str(record_k[j]) + "位置从" + str(record_v[j][_p]) + '变为' + str(info_car[i][_p]),
    #                       info_car[i])
    #                 info_car[i].append(record_v[j][_v])
    #                 record_v[j] = info_car[i]
    #                 vDeleteTime[j] = time.time() * 1000
    #                 info_car[i] = []
    #             break
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

            if distance_flag:
                print("##",info_car)
                print(record_v[small_index],info_car[i])
                print("相邻匹配相邻车道" + '通道' + str(record_v[small_index][_ch]) + "变为" + str(info_car[i][_ch]),
                      "车辆" + "位置从" + str(record_v[small_index][_p]) + '变为' + str(info_car[i][_p]), info_car[i])
                info_car[i].append(record_v[small_index][_v])
                record_v[small_index] = info_car[i]
                info_car[i] = []

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
                        _p]:
                        tmp = new_record_v[j]
                        new_record_v[j] = new_record_v[i]
                        new_record_v[i] = tmp
                        print("位置匹配错误，已更改", tmp, "改为", new_record_v[j])

    for i in range(len(new_record_v)):
        if new_record_v[i] != former_record_v[i]:

            if new_record_v[i][_ch] != former_record_v[i][_ch]: #变道
                line_change[i].append(copy.deepcopy(former_record_v)) #存入变道之前位置
                line_change[i].append(copy.deepcopy(new_record_v[i]))

            if len(line_change[i]) != 0:
                if len(line_change[i])>3:
                    if kType[i]==0: #小车变成大车
                        car_position_count = 0
                        for history_car_position in line_change[i][0]:
                            if history_car_position[_ch]==line_change[i][0][i][_ch] and kType[car_position_count]==1:
                                history_distance = history_car_position[_p]-line_change[i][0][i][_p]
                                # if line_change[i][0][i][_v]*history_distance<0 and abs(history_distance)<20:
                                if abs(history_distance) < 25:
                                    print("小车变道出现错误","小车变道点为",line_change[i][0][i],"小车已经行驶到",line_change[i][-1]
                                          ,"最近的大车历史位置为", line_change[i][0][car_position_count], '最近大车已经行驶到',new_record_v[car_position_count])
                                    car_position_tmp = new_record_v[i] #小车定位
                                    new_record_v[i] = new_record_v[car_position_count]
                                    new_record_v[car_position_count] = car_position_tmp
                                    print("位置纠正，清空小车变道信息")
                                    line_change[i] = []
                                else:
                                    print("小车变道点出现问题，没有找到合适的点进行纠正",line_change[i][0][i],"小车已经行驶到",line_change[i][-1],
                                          "变道点所有车辆信息为",line_change[i][0])
                            car_position_count+=1 #自增点确定车辆类型

                    # if kType[i] ==1: #


                if new_record_v[i] != line_change[i][-1] and new_record_v[i][_car_type]!=kType[i]: #车型不一致
                    time_remove_list = []
                    for time_index in range(len(line_change[i])):
                        if time_index>0 and new_record_v[i][_t] - line_change[i][time_index][_t]> 2000: #大于2s移掉的
                            time_remove_list.append(time_index)
                    for time_remove in time_remove_list:
                        line_change[i].remove(line_change[i][time_remove])
                    line_change[i].append(copy.deepcopy(new_record_v[i]))

                    if new_record_v[i][_t] - line_change[i][0][i][_t]>10000:
                        print("变道时间超过了10s仍符合条件，清空此次变道信息")
                        line_change[i] = []

            # vDeleteTime[i] = time.time() * 1000
            # car_his_pos[i].append(copy.deepcopy(new_record_v[i][_p]))
            # car_his_pos_time[i].append(copy.deepcopy(new_record_v[i][_t]))
            # if len(car_his_pos[i]) >= 10:
            #     new_record_v[i][_v] = is_average_position(np.array(car_his_pos[i][-10:]), car_his_pos_time[i][-10:])
            # else:
            #     print('没有存够位置进行速度更新', car_his_pos[i], car_his_pos_time[i])


if __name__ == '__main__':
    print(55 / 1000)
    _ch = 0  # 通道号
    _p = 1  # 位置
    _scope = 3  # 范围
    _t = 5  # 时间
    _car_type = 4
    _v = 6
    start= 10024
    _max_time_limited = 0.2  # 0.5滑窗设为0.5  0.1设为0.1
    _min_time_limited = 0.01
    line_change = [[], [], [], [], [], [[[3, 10255, 0.1262182891368866, [10245, 10260], 0, 1650006736093, 13.720565157275805], [3, 10200, 0.10802508145570755, [10189, 10205], 0, 1650006736093, 14.16164354059708], [2, 10164, 0.28421199321746826, [10159, 10169], 0, 1650006736093, 5.511690203443536], [2, 10149, 1.3841867446899414, [10144, 10154], 1, 1650006735537, 10.500616136208546], [2, 10109, 0.183089017868042, [10104, 10114], 0, 1650006736093, 5], [2, 10094, 2.8185462951660156, [10084, 10099], 1, 1650006735158, 13.65765466929679], [3, 10114, 0.17002858221530914, [10104, 10119], 0, 1650006736093, 39.95793457079942]], [3, 10099, 0.401888370513916, [10094, 10104], 0, 1650006736280, 13.65765466929679], [3, 10104, 0.5260396599769592, [10094, 10109], 0, 1650006736469, 10.255212851873488], [3, 10104, 0.5260396599769592, [10094, 10109], 0, 1650006736660, 9.564717955220642], [3, 10104, 0.5260396599769592, [10094, 10109], 0, 1650006736850, 8.54265309630329], [3, 10109, 0.22085216641426086, [10099, 10114], 0, 1650006737039, 7.142317248429797], [3, 10109, 0.22085216641426086, [10099, 10114], 0, 1650006737225, 7.2785453726998846], [3, 10114, 0.4014866054058075, [10109, 10119], 0, 1650006737410, 6.913980389674164], [3, 10114, 0.4014866054058075, [10109, 10119], 0, 1650006737602, 6.514634170743369], [3, 10119, 0.4198859930038452, [10114, 10129], 0, 1650006737976, 7.43670841274853], [3, 10119, 0.4198859930038452, [10114, 10129], 0, 1650006738160, 9.15600174990302]], [], []]
    kType = [0, 0, 0, 1, 0, 1, 0, 0]
    k = [1,2,3,4,5,6,7,8]
    v = [[3, 10280, 0.1560562551021576, [10275, 10285], 0, 1650006738160, 13.990779622288466], [3, 10230, 0.16946206986904144, [10225, 10235], 0, 1650006738160, 13.902353501628655], [2, 10179, 0.5333974361419678, [10169, 10184], 0, 1650006738160, 8.667529832011262], [2, 10149, 1.3841867446899414, [10144, 10154], 1, 1650006738160, 5], [2, 10134, 1.663649082183838, [10129, 10144], 1, 1650006738160, 14.476900204114827], [3, 10119, 0.4198859930038452, [10114, 10129], 0, 1650006738160, 10.703059324508322], [3, 10144, 0.253854364156723, [10134, 10149], 0, 1650006738160, 13.139436694406296], [3, 10008, 0.11317998915910721, [10003, 10033], 0, 1650006738160, 4.420866489832007]]
    gg = copy.deepcopy(v)

    map_data= [[1, 10194, 1.1789871454238892, [10189, 10205], 1, 1650006738342], [1, 10069, 0.16741201281547546, [10064, 10074], 0, 1650006738342], [2, 10144, 5.911184787750244, [10134, 10149], 1, 1650006738342], [3, 10280, 0.1430085450410843, [10275, 10290], 0, 1650006738342], [3, 10230, 0.17716160416603088, [10225, 10240], 0, 1650006738342], [3, 10144, 2.060805320739746, [10139, 10149], 1, 1650006738342], [3, 10124, 0.47734877467155457, [10119, 10129], 0, 1650006738342], [3, 10104, 0.26916199922561646, [10094, 10109], 0, 1650006738342]]
    is_cross_match(k,v,map_data,kType)
    is_path_judge(gg,v)
    # is_smalldistance(k,v,map_data)


