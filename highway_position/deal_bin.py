import os

import numpy as np
import matplotlib.pyplot as plt
import train_data

plt.rcParams['font.size'] = 16
plt.rcParams['font.family'] = ['Fangsong']

# 采样频率
simpleFre = 1000
channel_num = 4

# 不同通道 传感器个数 不一样的 问题？？？     数据 形式 这么看    (4, 230, 1000)    高 宽  1000个点 才能体现信息
# 一秒内四个通道数据看作 一张图片 (4, 1000, 230)  -> (4, 230, 1000)   以最小传感器个数为基准 取后230个传感器数据
# 如何进行 真实框（线）的 标注？  和图片 的坐标原点 不一致的问题？  按照 右下角 左上角 坐标  标注 为 xmin ymin  xmax ymax ？？？
# 如何 将其调整为符合网络的输入？
# 网络训练过程loss 计算 和 网络预测 简化？？
# 待发现问题？？？？

path_total = 'E:/高速相关数据/2022.1.13'
save_path = path_total + '/npz/'  # 保存 npz 格式 数据 的 路径
if not os.path.exists(save_path):
    os.mkdir(save_path)

channel_list = ['CH1', 'CH2', 'CH3', 'CH4']  # 处理 几个 通道 的 数据

# (4, num_bin)  选取 最小 传感器数量  作为 基准    标准化  四个通道  数据形状
bin_file, sensor_num_min = train_data.get_bin_absolute_path(path_total, channel_list)
num_bin = bin_file.shape[1]  # 每个通道 的 bin 文件个数
print(f'每个通道有{num_bin}个bin文件')


for i in range(36, num_bin):
    """
        下次 运行  应该 从 20220113123800.bin  即 i = 39 开始 
        注意 修改
    """
    # 大小车 的 情况 似乎 有 别的车的  干扰    应该要对着 工况 挑 数据的
    # i = 0 1 2 3 4 ... 19 20 21       84  85  86 处理完成
    bin_one_minute = bin_file[:, i]  # 4个通道 某一分钟 的 bin 文件 （绝对路径）
    bin_name_minute = bin_one_minute[0].split('/')[-1].split('_')[-1]

    # 当前分钟 bin 文件 对应 的 真实线段（车辆） 数量  为 0 即 无真实线段 标注    跳过当前分钟
    num_gt = int(input(f'当前{bin_name_minute}文件 对应 的 真实线段（车辆） 数量（为0表示无车辆，跳过该bin文件）：'))
    if num_gt == 0:
        continue

    print('-' * 50)
    print(f'4个通道的{bin_name_minute}文件加载')
    data_one_minute = train_data.get_one_minute_data(bin_one_minute, sensor_num_min, simpleFre)
    print(data_one_minute.shape)   # (4, sensor_num_min, 60000)  看作一副图像  (高 宽 通道数) 如何标注？ 线段 两个端点 + 类别？
    print('')

    second_list = np.arange(0, 60 * simpleFre, 1000)  # [0, 1000, 2000, ..., 59000]

    for second in range(len(second_list)):
        print('*' * 25)
        print(f'开始处理{bin_name_minute}文件的第{second}秒的数据')
        if second + 1 == len(second_list):  # 最后 1s
            data_one_second = data_one_minute[:, :, second_list[second]:]  # (4, 234, 1000)
        else:
            data_one_second = data_one_minute[:, :, second_list[second]:second_list[second + 1]]  # 当前分钟 当前秒 的数据

        gt_boxes = []
        # 当前 分钟bin文件数据 一定 有 对应的 真实 线段（有车）
        for j in range(num_gt):
            print(f'对第{j}个真实线段进行位置标注（优先采用xmin、xmax（从1开始）形式）：')

            x1 = input('     第一个端点x（宽）坐标（输入 -1 代表跳过当前真实线段标注！！）：')
            if x1 == '':
                x1 = input('     重新输入  第一个端点x（宽）坐标：')
            elif x1 == '-1':
                print(f'跳过第{j}个真实线段的位置标注')
                continue
            y1 = input('     第一个端点y（高）坐标：')
            if y1 == '' or data_one_second.shape[0] < int(y1) or int(y1) < 1:
                y1 = input('     重新输入  第一个端点y（高）坐标：')

            x2 = input('     第二个端点x（宽）坐标：')
            if x2 == '':
                x2 = input('     重新输入  第二个端点x（宽）坐标：')
            y2 = input('     第二个端点y（高）坐标：')
            if y2 == '' or data_one_second.shape[0] < int(y2) or int(y2) < 1:
                y2 = input('     重新输入  第二个端点y（高）坐标：')

            cls = input('     当前线段对应的车类别索引（0为car、1为bigcar）：')
            if cls not in ['0', '1']:
                cls = input('     重新输入  当前线段对应的车类别索引：')

            gt_boxes.append(list(map(int, [x1, y1, x2, y2, cls])))

        gt_boxes = np.array(gt_boxes)  # (num_gt, 5)

        # 保存 当前秒  原始数据 （有正 有负） 及  手动标注的 车 位置数据   这就是 一张 带标注的 训练 图片
        if len(gt_boxes) != 0:

            npz_name = bin_name_minute.split('.')[0] + '_' + str(second) + '.npz'
            np.savez_compressed(save_path + npz_name, image=data_one_second, box=gt_boxes)
            print(f'{bin_name_minute}文件的第{second}秒的数据处理完成！')
            print('*' * 25)
            print('')
        else:
            print(f'{bin_name_minute}文件的第{second}秒的数据无效（无用或有干扰数据）！！！')
            print('*' * 25)
            print('')

    print('-' * 50)
    print(' ')
