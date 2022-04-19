import numpy as np
import pandas as pd
import tensorflow as tf
import tensorflow_addons as tfa
from sklearn.model_selection import train_test_split
from tensorflow.keras import optimizers, losses, callbacks

from model_test import get_model


def preprocess(feature, label):
    # [0~255] -> [0~1] -> [-1~1]  像素值范围
    # feature = 2 * tf.cast(feature, dtype=tf.float32) / 255. - 1.
    label = tf.one_hot(tf.cast(label, dtype=tf.int32), depth=num_classes)
    return feature, label


data1 = pd.read_csv('E:/高速相关数据/2022.1.13/dataset_raw_1000_20220113115900.bin.csv', header=None).dropna().values
# data2 = pd.read_csv('E:/高速相关数据/2022.1.13/dataset_raw_1000_20220113121800.bin.csv', header=None).values
data3 = pd.read_csv('E:/高速相关数据/2022.1.13/dataset_raw_1000_20220113132300.bin.csv', header=None).values
x1 = data1[:, :-1]
y1 = data1[:, -1]
x1 = x1[y1 == 1]
y1 = y1[y1 == 1]

x3 = data3[:, :-1]
y3 = data3[:, -1]
x3 = x3[y3 == 1]
y3 = y3[y3 == 1] - 1
#
# data = np.vstack((data1, data2, data3))    单大车     单小车
data = pd.read_csv('E:/高速相关数据/2022.1.13/dataset_raw_1000_20220113131100.bin.csv', header=None).values
print(data.shape)

x = data[:, :-1]
x = np.vstack((x, x1, x3))

x = np.expand_dims(x, axis=2)
print(x.shape)
# print(np.any(np.isnan(x)))  # 判断 是否 有 nan

y = data[:, -1]
y = np.hstack((y, y1, y3))
num_classes = len(np.unique(y))

# 划分 训练集 验证集   (及 测试集 )
x_train, x_val, y_train, y_val = train_test_split(x, y, test_size=0.3, random_state=320)
# x_train, x_val, y_train, y_val = train_test_split(x_train, y_train, test_size=0.3, random_state=22)

train_db = tf.data.Dataset.from_tensor_slices((x_train, y_train))
train_db = train_db.shuffle(10000).map(preprocess).batch(256)  # drop_remainder为true时 即将最后一个不满足128的batch丢弃掉

val_db = tf.data.Dataset.from_tensor_slices((x_val, y_val))
val_db = val_db.map(preprocess).batch(256)

# test_db = tf.data.Dataset.from_tensor_slices((x_test, y_test))
# test_db = test_db.map(preprocess).batch(128)

model = get_model(input_shape=(None, x.shape[1], 1), num_classes=num_classes, dense_act='softmax',
                  model_path='multi_ep043-val_acc0.966-val_f10.956.h5')

# 在数据不平衡的情况下，准确率并不是衡量分类器性能的最佳指标
# 在测量精确率和召回率方面，没有任何一种不平衡校正技术可以 与  增加更多的训练数据相媲美。

# 为了同时兼顾精确度和召回率，我们创造了两者的调和平均数作为考量两者平衡的综合性指标，称之为F1 measure。
# 两个数之间的调和平均倾向于靠近两个数中比较小的那一个数，因此我们追求尽量高的F1 measure，能够保证我们的精确度和召回率都比较高。
# F1 measure在[0,1]之间分布，越接近1越好。      二分类的micro-F1 score和Accuracy的值相等    常用的是Macro-F1
model.compile(optimizer=optimizers.Adam(learning_rate=1e-4),
              loss=losses.CategoricalCrossentropy(),
              metrics=['accuracy', tfa.metrics.F1Score(num_classes=num_classes, average='macro')])

checkpoint = callbacks.ModelCheckpoint('weights/ep{epoch:03d}-val_acc{val_accuracy:.3f}-val_f1{val_f1_score:.3f}.h5',
                                       monitor='val_f1_score', save_weights_only=True, save_best_only=True, mode='max')

early_stopping = callbacks.EarlyStopping(monitor='val_f1_score', patience=200, mode='max')
history = model.fit(train_db, epochs=2000, validation_data=val_db, callbacks=[early_stopping, checkpoint])

# print(history.history)
# model.evaluate(test_db)
#
#
# t1 = time.time()
# model(x_test[:1])
# print('耗时：', time.time() - t1)
