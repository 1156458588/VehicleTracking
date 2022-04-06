import numpy as np

data_frame = [[[1, 2, 3, 4], [100, 101, 102, 103]],
              [[5, 6, 7, 8], [100, 101, 102, 103]],
              [[9, 10, 11, 12], [100, 101, 102, 103]]]
data_frame = np.array(data_frame)
print(data_frame.shape)
data_frame = np.concatenate(data_frame, axis=0)

print(data_frame.shape)
print([[] for i in range(4)])
