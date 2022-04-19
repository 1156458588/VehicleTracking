def is_cross_match(record_k, record_v, info_car):
    def judge_condition_cross(x, y):
        flag = False
        if len(x) == 0 or x[_max] == 0:
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
        if len(x) == 0 or x[_max] == 0:
            return False
        if 1000 * _max_time_limited * 20 > x[_t] - y[
            _t] >= _min_time_limited * 1000 and ((x[_p] - y[_p]) / (x[_t] - y[_t])) * y[_v] > 0:
            # 判断预测条件
            return True

    # 同个车道匹配

    # 匹配同车道
    for i in range(len(info_car)):
        for j in range(len(record_v)):
            if judge_condition_cross(info_car[i], record_v[j]) and record_v[j][_ch] == info_car[i][_ch] and record_v[j][
                _p] > start:
                if ((info_car[i][_p] - record_v[j][_p]) / (info_car[i][_t] - record_v[j][_t])) * record_v[j][_v] >= 0:
                    if info_car[i][_p] - record_v[j][_p] != 0:
                        print("交叉匹配同车道" + "车辆" + str(record_k[j]) + "位置从" + str(record_v[j][_p]) + '变为' + str(
                            info_car[i][_p]), info_car[i])
                        info_car[i].append(record_v[j][_v])
                        record_v[j] = info_car[i]
                        vDeleteTime[j] = time.time() * 1000
                    else:
                        record_v[j][_t] = info_car[i][_t]
                        vDeleteTime[j] = time.time() * 1000
                        print("位置重复出现,只更新时间")
                else:
                    vDeleteTime[j] = time.time() * 1000
                    print("交叉匹配同车道出现位置倒退，只更新时间", record_v[j], info_car[i])
                    record_v[j][_t] = info_car[i][_t]
                info_car[i] = []
                break

    for i in range(len(info_car)):
        small_distance = 30
        small_index = -1
        for j in range(len(record_v)):
            if judge_condition_small(info_car[i], record_v[j]) and record_v[j][_ch] == info_car[i][_ch]:
                if abs(info_car[i][_p] - record_v[j][_p]) < small_distance * ((
                                                                                      info_car[i][_t] - record_v[j][
                                                                                  _t] + 1000) // 1000):
                    small_distance = abs(info_car[i][_p] - record_v[j][_p])
                    small_index = j
        if small_index != -1:
            print("相邻匹配同车道" + "车辆" + str(record_k[small_index]) + "位置从" + str(record_v[small_index][_p]) + '变为' + str(
                info_car[i][_p]), info_car[i])
            info_car[i].append(record_v[small_index][_v])
            record_v[small_index] = info_car[i]
            vDeleteTime[small_index] = time.time() * 1000
            info_car[i] = []


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
        small_distance = 30
        small_index = -1
        for j in range(len(record_v)):
            if judge_condition_small(info_car[i], record_v[j]) and abs(
                    record_v[j][_ch] - info_car[i][_ch]) == 1:
                if abs(info_car[i][_p] - record_v[j][_p]) < small_distance:
                    small_distance = abs(info_car[i][_p] - record_v[j][_p])
                    small_index = j
        if small_index != -1:
            for n in range(len(record_v)):
                if (info_car[i][_p] - record_v[n][_p]) * (record_v[small_index][_p] - record_v[n][_p]) < 0:
                    print("相邻匹配出现位置重叠", info_car[i], record_v[small_index], record_v[n])
                    info_car[i] = []
                    break
            print("相邻匹配相邻车道" + '通道' + str(record_v[small_index][_ch]) + "变为" + str(info_car[i][_ch]),
                  "车辆" + "位置从" + str(record_v[small_index][_p]) + '变为' + str(info_car[i][_p]), info_car[i])
            info_car[i].append(record_v[small_index][_v])
            record_v[small_index] = info_car[i]
            vDeleteTime[small_index] = time.time() * 1000
            info_car[i] = []
    return record_k, record_v, info_car