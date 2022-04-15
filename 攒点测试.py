#
#
# def zanDian():
#     # 在最开始获取数组长度
#     length = len(foreCastAndBianDaoStack)
#     for c in car:
#         pushFlag = False
#         if len(c) > 0 and c[cPotition] != 0:
#             for i in range(length):
#                 if 0 < c[cPotition] - foreCastAndBianDaoStack[i][-1][cPotition] < zanDianThreshold and c[cTongDao] == foreCastAndBianDaoStack[i][-1][cTongDao] and len(foreCastAndBianDaoStack[i]) <= zanDianNeedNum:
#                     foreCastAndBianDaoStack[i].append(c)
#                     pushFlag = True
#             if not pushFlag:
#                 foreCastAndBianDaoStack.append([c])
#
# if __name__ == '__main__':
#     vTime = 5  # v中存放时间的索引
#     vSpeed = 6  # v中存放速度的索引
#     vPosition = 1  # v中存放定位的索引
#     vScope = 3  # v中存放范围的索引
#     vCartype = 4  # v中存放车型的索引
#     vTongDao = 0  # v中存放车型的索引
#     # car
#     cCartype = 4  # car中存放车型的索引
#     cTime = 5  # car中存放时间的索引
#     cPotition = 1  # car中存放定位的索引
#     cScope = 3  # car中存放范围的索引
#     cTongDao = 0  # car中存放通道的索引
#     pushT = 0
#     car = []
#     vDeleteTime = []
#     cStackDeleteTime = []
#     t = 0
#     # 车辆入口
#     start = 10048
#     end = 9998
#     entrance = [i for i in range(end, start)]
#
#     car_his_pos = []
#     car_his_pos_time = []
#     zhiXingDu = 0.9
#     chuKou = 10698
#     foreCastAndBianDaoStack = []
#     zanDianNeedNum = 1
#     zanDianThreshold = 35
#
#     car = [[2, 10285, 265.4651184082031, [10275, 10290], 1, 1649644231082], [], [2, 10290, 265.4651184082031, [10275, 10290], 1, 1649644231082]]
#     zanDian()
#     car = [[2, 10286, 265.4651184082031, [10275, 10290], 1, 1649644231082], [2, 10294, 265.4651184082031, [10275, 10290], 1, 1649644231082], [2, 0, 265.4651184082031, [10275, 10290], 1, 1649644231082]]
#     zanDian()
#     print(foreCastAndBianDaoStack)