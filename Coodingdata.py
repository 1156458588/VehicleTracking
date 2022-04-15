import csv
import copy


def MapLane(lane):
    if lane == 'Y1':
        return 0
    elif lane == 'Y2':
        return 1
    elif lane == 'Y3':
        return 2
    elif lane == 'Y4':
        return 3
    elif lane == 'Z1':
        return 4
    elif lane == 'Z2':
        return 5
    elif lane == 'Z3':
        return 6
    elif lane == 'Z4':
        return 7


class RoadEncoder(object):
    def __init__(self, filepath='2.csv', lanes=8):
        self.EncodDict = {}
        self.lanes = lanes
        self.LaneData = [None] * lanes
        self.LaneCars = [-1] * lanes
        self.CurTimestamp = 0
        self.L_Data = []
        self.mil_range = [None] * 8  # 当前编码表中各车道最大最小里程
        self.LoadCodingSheet(filepath)

    def ResetLaneData(self):
        self.LaneData = [None] * self.lanes
        self.LaneCars = [-1] * self.lanes
        self.CurTimestamp = 0

    def LoadCodingSheet(self, filepath):
        min_mil = [999999] * 8
        max_mil = [0] * 8
        csv_file = open(filepath, "r")
        reader = csv.reader(csv_file)
        for item in reader:
            self.EncodDict['-'.join(item[0:3])] = '-'.join(item[3:5])
            lane = MapLane(item[3])
            mil = int(item[4])
            if min_mil[lane] > mil:
                min_mil[lane] = mil
            if max_mil[lane] < mil:
                max_mil[lane] = mil
        for i in range(len(self.mil_range)):
            self.mil_range[i] = [min_mil[i], max_mil[i]]
        pass

    def MappingData(self, data):
        data = list(data)
        cars = data[7]
        if cars > 0:
            data[1] = data[1]+1
            key_sensor = '-'.join(map(str, data[0:3]))
            key_min_sensor = '-'.join(map(str, [data[0], data[1], data[4]]))
            key_max_sensor = '-'.join(map(str, [data[0], data[1], data[5]]))
            val_mil = self.EncodDict.get(key_sensor)
            val_min_mil = self.EncodDict.get(key_min_sensor)
            val_max_mil = self.EncodDict.get(key_max_sensor)
            if val_mil is not None and val_min_mil is not None and val_max_mil is not None:
                f_range = [int(val_min_mil.split('-')[1]), int(val_max_mil.split('-')[1])]
                mil_range = [min(f_range), max(f_range)]
                mil_data = val_mil.split('-')
                mil_data = mil_data + [data[3]]
                mil_data.append(mil_range)
                mil_data.extend([data[6], data[8]])
                mil_data[0] = MapLane(mil_data[0])
                mil_data[1] = int(mil_data[1])
                self.LaneCars[mil_data[0]] = cars
                return self.SyncDataTime(mil_data)
            else:
                raise Exception('映射表中无对应信息！')
        else:
            mil_data = [data[1], 0, 0, [0, 0], 0, data[8]]
            # self.LaneCars[mil_data[0]] = cars
            return self.SyncDataTime(mil_data)

    def SyncDataTime(self, mil_data):
        lane_index = mil_data[0]
        if self.CurTimestamp == 0:
            self.CurTimestamp = mil_data[5]
            # self.LaneData[lane_index] = mil_data
            self.L_Data.append(mil_data)
            print("加入")
            return None
        else:
            if abs(mil_data[5] - self.CurTimestamp) < 160:
                mil_data[5] = self.CurTimestamp
                self.L_Data.append(mil_data)
                # if self.LaneData[lane_index] is None:
                #     self.LaneData[lane_index] = [mil_data]
                # else:
                #     self.LaneData[lane_index].append(mil_data)
                print("加入")
                return None
            else:
                new_data = copy.deepcopy(self.L_Data)
                self.L_Data.clear()
                self.CurTimestamp = mil_data[5]
                self.L_Data.append(mil_data)
                return new_data
                # for i in range(self.lanes):
                #     if self.LaneCars[i] == -1 or self.LaneData[i] is None:
                #         self.ResetLaneData()
                #         return None
                    # if self.LaneCars[i] == -1:
                    #     self.ResetLaneData()
                    #     return None
                    # elif self.LaneData[i] is None:
                    #     self.ResetLaneData()
                    #     return None
                    # elif len(self.LaneData[i]) != self.LaneCars[i]:
                    #     self.ResetLaneData()
                    #     return None
                #     else:
                #         continue
                # new_data = copy.deepcopy(self.LaneData)
                # self.ResetLaneData()
                # return new_data
