# -*- coding: utf-8 -*-

"""
配置参数信息
"""

Config = {
    "model_path": "../Output",
    "train_data_path": "../Data/train_tag_review.json",
    "valid_data_path": "../Data/valid_tag_review.json",
    "vocab_path":"chars.txt",
    "model_type":"rnn",
    "class_num": 2,
    "max_length": 20,
    "hidden_size": 6,
    "kernel_size": 3,
    "num_layers": 1,
    "epoch": 15,
    "batch_size": 96,
    "pooling_style":"max",
    "optimizer": "adam",
    "learning_rate": 1e-3,
    "pretrain_model_path":r"F:\Desktop\work_space\pretrain_models\bert-base-chinese",
    "seed": 987
}