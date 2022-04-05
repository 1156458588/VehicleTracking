# def initialCars(car):
#     global car_num
#     global usedRecord
#     global vt
#
#     for messageNo in car:
#         if len(messageNo) == 0:
#             continue
#         pushFlag = False
#         for i in range(len(carStack) - 1, -1, -1):
#             if messageNo not in usedRecord and isDuplicated(messageNo[cPotition], carStack[i][-1][cPotition]):
#                 usedRecord.append(messageNo)
#                 continue
#             if messageNo not in usedRecord and (
#                     (Iou(messageNo[cScope], carStack[i][-1][cScope]) and not isDuplicated(messageNo[cPotition],
#                                                                                           carStack[i][-1][
#                                                                                               cPotition]) and messageNo[
#                          cTongDao] == carStack[i][-1][cTongDao])
#                     or
#                     (Distance(messageNo[cPotition], carStack[i][-1][cPotition], threshold) and not isDuplicated(
#                         messageNo[cPotition], carStack[i][-1][cPotition]) and messageNo[cTongDao] == carStack[i][-1][
#                          cTongDao])
#             ):
#                 if len(carStack[i]) >= initialNum:
#                     curP = messageNo[cPotition]
#                     lastP = carStack[i][-1][cPotition]
#                     # lastSecond = carStack[i][-1][cPotition]
#                     print('lastP = ', lastP)
#                     vt = ((curP - lastP) / abs(curP - lastP)) * vt
#                     vt = 69
#                     k.append(str(uuid.uuid1()))
#                     temp = messageNo
#                     temp.append(vt)
#                     v.append(temp)
#                     pushFlag = True
#                     car_num += 1
#                     print("删除:", carStack[i])
#                     carStack.remove(carStack[i])
#                     usedRecord.append(messageNo)
#                 else:
#                     carStack[i].append(messageNo)
#                     pushFlag = True
#                     usedRecord.append(messageNo)
#         # 匹配失败则新建一条记录
#         if not pushFlag and messageNo not in usedRecord:
#             new = [messageNo]
#             carStack.append(new)
#         usedRecord.append(messageNo)
#     usedRecord = []