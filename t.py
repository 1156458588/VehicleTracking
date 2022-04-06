import numpy as np

from match import getClean

if __name__ == '__main__':
    maxK = []
    x = [[0.07478343441611841, 8], [0.05920355224609375, 8], [0, 0], [0.7269868489583333, 8], [0, 0]]
    for i in x:
        maxK.append(i[0])
    carIndex, gaiLv = getClean(x)
    vIndex = []
    for g in gaiLv:
        vIndex.append(np.where(np.array(maxK) == g)[0])
    print(vIndex)
    for i in range(len(gaiLv)):
        print('index = ', vIndex[i])
        if len(vIndex[i]) > 1:
            vNo = vIndex[i][0]
        else:
            vNo = int(vIndex[i])
        print('vNo = ', vNo)
        print('第' + str(vNo) + '个车以概率' + str(gaiLv[i]) + '到达')