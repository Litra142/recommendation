# -*- coding: utf-8 -*-
import math
import random
from operator import itemgetter

REC_NUMBER = 10
similarity_user = 70


def SplitData(filename, M, seed):           #读取数据，分割为训练集和测试集：M表示 1/M 的样本为测试集
    test = dict()
    train = dict()                          #数据集以dict的方式存储，key为user id， value为user看过的movie id组成的list
    random.seed(seed)
    with open(filename,'r') as f:
        for i, line in enumerate(f):
            if i == 0:
                continue
            user, movie, rating, timestamp = line.split('::')
            user = int(user)
            if float(rating) < 4:                   #此处int(rating)会报错；4分以下的评分忽略
                continue
            if random.randint(1,M) == 1:
                if user not in test:
                    test[user] = []
                test[user].append(movie)
            else:
                if user not in train:
                    train[user] = []
                train[user].append(movie)
    return test, train



def UserSimilarity(train):
    #build inverse table for item_users: it's shown that each item was selected by which users
    item_users = {}
    for u, items in train.items():
        for i in items:
            if i not in item_users:
                item_users[i] = []
            item_users[i].append(u)

    user_sim_matrix = {}
    for i, users in item_users.items():
        for u in users:
            for v in users:
                if u == v:
                    continue
                user_sim_matrix.setdefault(u, {})
                user_sim_matrix[u].setdefault(v, 0)
                user_sim_matrix[u][v] += 1

    #calculate finial similarity matrix W
    for u, related_users in user_sim_matrix.items():
        for v, cuv in related_users.items():
            user_sim_matrix[u][v] = cuv / math.sqrt(len(train[u]) * len(train[v]))
    return user_sim_matrix

def Recommend(user, train, W):
    rank = dict()
    n = REC_NUMBER
    k = similarity_user
    watched_items = train[user]
    for v, wuv in sorted(W[user].items(),key=itemgetter(1), reverse=True)[:k]:      #obtained most k user which similarity given user
        for movie in train[v]:
            if movie in watched_items:
                continue
            rank.setdefault(movie, 0)
            rank[movie] += wuv
    #return most n movies which have large probability given user will like these. Return type: [{movieID: similarity score}, {},...,{}]
    return sorted(rank.items(), key=itemgetter(1), reverse=True)[:n]


class Evaluation():

    def __init__(self, train, test, W):
        self.train = train
        self.test = test
        self.W = W
        self.N = REC_NUMBER
        self.hit = 0
        self.all = 0
        self.recommend_items = set()
        self.all_items = set()

    def run(self):
        for user in self.train.keys():
            for item in self.train[user]:
                self.all_items.add(item)
            tu = self.test.get(user, {})  # user corresponding movie list in the test.
            rank = Recommend(user, self.train, self.W)
            for item, _ in rank:
                if item in tu:
                    self.hit += 1
                self.recommend_items.add(item)
            self.all += len(tu)

    def Recall(self):
        return self.hit / (self.all * 1.0)

    def Precision(self):
        return self.hit / (len(self.train) * self.N * 1.0)

    def Coverage(self):
        return len(self.recommend_items) / (len(self.all_items) * 1.0)



if __name__ == '__main__':
    filename = '/home/ssw/coding/Python_project/recommendation/ml-latest-small/ratings.csv'
    test, train = SplitData(filename, 5, random.random())
    W = UserSimilarity(train)
    result = Evaluation(train, test, W)
    result.run()
    print('precision: ', result.Precision())
    print('recall: ', result.Recall())
    print('coverage ', result.Coverage())