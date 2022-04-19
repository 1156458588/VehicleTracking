from tensorflow.keras import layers, Sequential


def get_model(input_shape, model_path=None):
    """
    得到 模型
    :return:
    """
    model = Sequential([
        # (b, 750, 1) -> (b, 375, 32)    第一层的filter, 数量不要太少. 否则根本学不出来(底层特征很重要).
        layers.Conv1D(64, 3, strides=2, padding='valid'),  # param = 32*1 * 32 + 32 = 1056
        layers.BatchNormalization(),
        layers.ReLU(),
        # layers.MaxPooling1D(pool_size=2, strides=2),
        # (b, 375, 32) -> (b, 187, 64)
        layers.Conv1D(128, 3, strides=2, padding='valid'),  # param = 2*32 * 64 + 64 = 4160
        layers.BatchNormalization(),
        layers.ReLU(),
        # layers.MaxPooling1D(pool_size=2, strides=2),
        # (b, 187, 64) -> (b, 93, 128)
        layers.Conv1D(256, 3, strides=2, padding='valid'),  # param = 2*64 * 128 + 128 = 16512
        layers.BatchNormalization(),
        layers.ReLU(),
        # layers.MaxPooling1D(pool_size=2, strides=2),

        layers.GlobalAveragePooling1D(),
        layers.Dropout(rate=0.22),
        layers.Dense(2, activation='sigmoid'),

    ])
    model.build(input_shape=input_shape)

    if model_path:   # 传入 path 时  加载权重文件
        model.load_weights(model_path)

    return model


if __name__ == '__main__':
    model = get_model((None, 1000, 1))
    model.summary()



