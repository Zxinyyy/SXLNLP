# -*- coding: utf-8 -*-

import torch
import torch.nn as nn
from torch.optim import Adam, SGD
from torch.nn.utils.rnn import pack_padded_sequence, pad_packed_sequence
"""
建立网络模型结构
"""

class SentenceEncoder(nn.Module):
    def __init__(self, config):
        super(SentenceEncoder, self).__init__()
        hidden_size = config["hidden_size"]
        vocab_size = config["vocab_size"] + 1
        max_length = config["max_length"]
        self.embedding = nn.Embedding(vocab_size, hidden_size, padding_idx=0)
        # self.lstm = nn.LSTM(hidden_size, hidden_size, batch_first=True, bidirectional=True)
        self.layer = nn.Linear(hidden_size, hidden_size)
        self.dropout = nn.Dropout(0.5)

    #输入为问题字符编码
    def forward(self, x):
        x = self.embedding(x)
        #使用lstm
        # x, _ = self.lstm(x)
        #使用线性层
        x = self.layer(x)
        # 对调换后的张量应用一维最大池化，池化窗口大小等于调换后张量的第2维长度。
        x = nn.functional.max_pool1d(x.transpose(1, 2), x.shape[1]).squeeze()
        return x


class SiameseNetwork(nn.Module):
    def __init__(self, config):
        super(SiameseNetwork, self).__init__()
        self.sentence_encoder = SentenceEncoder(config)
        self.loss = self.cosine_triplet_loss

    # 计算余弦距离  1-cos(a,b)
    # cos=1时两个向量相同，余弦距离为0；cos=0时，两个向量正交，余弦距离为1
    def cosine_distance(self, tensor1, tensor2):
        '''
            计算余弦距离  1-cos(a,b)
            一个向量矩阵 与 第二个向量矩阵 对位相乘，批量计算相似度
        '''
        tensor1 = torch.nn.functional.normalize(tensor1, dim=-1) # batch x hidden_size
        tensor2 = torch.nn.functional.normalize(tensor2, dim=-1)
        
        # torch.mul: 逐元素对位相乘
        cosine = torch.sum(torch.mul(tensor1, tensor2), axis=-1) # batch x 1
        return 1 - cosine

    def cosine_triplet_loss(self, a, p, n, margin=None):
        '''
            L = max(d(a,p)-d(a,n)+margin, 0)
        '''
        ap = self.cosine_distance(a, p) # 1 x L
        an = self.cosine_distance(a, n)
        if margin is None:
            diff = ap - an + 0.1
        else:
            diff = ap - an + margin.squeeze()
            
        # 只对>0的三元组loss进行平均，即当 diff>0 时参与损失的计算。
        # 这避免了无意义的负损失对计算结果的影响。
        
        # diff.gt(0) 是 PyTorch 中的一种张量操作，用于生成一个布尔张量，指示 diff 张量中哪些元素大于零。
        return torch.mean(diff[diff.gt(0)]) #greater than

    #sentence : (batch_size, max_length)
    def forward(self, sentence1, sentence2=None, sentence3=None, target=None):
        #同时传入3个句子: anchor, positive, negative
        if sentence2 is not None and sentence3 is not None:
            vector1 = self.sentence_encoder(sentence1) #vec:(batch_size, hidden_size)
            vector2 = self.sentence_encoder(sentence2)
            vector3 = self.sentence_encoder(sentence3)
            #如果有标签，则计算loss
            if target is not None:
                return self.loss(vector1, vector2, vector3, target.squeeze())
            #如果无标签，计算余弦距离
            else:
                return self.cosine_distance(vector1, vector2)
        #单独传入一个句子时，认为正在使用向量化能力
        else:
            return self.sentence_encoder(sentence1)


def choose_optimizer(config, model):
    optimizer = config["optimizer"]
    learning_rate = config["learning_rate"]
    if optimizer == "adam":
        return Adam(model.parameters(), lr=learning_rate)
    elif optimizer == "sgd":
        return SGD(model.parameters(), lr=learning_rate)


if __name__ == "__main__":
    from config import Config
    Config["vocab_size"] = 50
    Config["max_length"] = 4
    model = SiameseNetwork(Config)
    # anchor
    s1 = torch.LongTensor([[1,2,3,0], [2,2,0,0]]) # batch_size=2, max_length=4
    # positive
    s2 = torch.LongTensor([[1,2,3,4], [3,2,3,4]])
    # negative
    s3 = torch.LongTensor([[9,8,7,6], [13,22,30,40]])
    l = torch.LongTensor([[1],[0]]) # batch_size=2
    
    y = model(s1, s2, s3, l)
    print(y)
    # print(model.state_dict())
