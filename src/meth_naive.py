import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset
import torchvision.transforms as transforms
from CNNTrainTestManager import CNNTrainTestManager, optimizer_setup
from models.AlexNet import AlexNet
from models.CNNVanilla import CnnVanilla
from models.ResNet import ResNet
from torchvision import datasets
from random import sample
import matplotlib.pyplot as plt
import os


class MyDataset(Dataset):

        def __init__(self, dataset):
            self.dataset = dataset

        def __getitem__(self, index):
            data, target = self.dataset[index]

            return data, target, index

        def __len__(self):
            return len(self.dataset)

class Naive_meth(object):

    def __init__(self, train_set, test_set, model_name, optimizer_factory, num_epochs=1, val_set=0.1, in_channels=3, batch_size=1, naive_meth = 'entropy'):
    
        self.train_set = MyDataset(train_set)
        self.test_set = MyDataset(test_set)
        self.model_name = model_name
        self.in_channels = in_channels
        self.batch_size = batch_size
        self.optimizer_factory = optimizer_factory
        self.val_set = val_set
        self.num_epochs = num_epochs
        self.naive_meth = naive_meth

    def run(self):

        print("Training using the naive active learning method with type {}".format(self.naive_meth))

        num_train = len(self.train_set)
        indexs = list(range(num_train))
        accuracies = []
        train_index = []

        for i in range(10):
            print("training on the number <{}> 10% of the dataSet.".format(i+1))
            if i+1 == 1:
                train_index += sample(indexs, int(num_train*0.1))
                indexs = [l for l in indexs if l not in train_index]
            elif i+1 == 10:
                train_index += indexs
            else:
                train_index += model_trainer.get_least_confidence(
                    trainset=self.train_set, testset=self.test_set, index_list=indexs, out_size=int(num_train*0.1), type=self.naive_meth)
                indexs = [l for l in indexs if l not in train_index]

            if self.model_name == 'CnnVanilla':
                model = CnnVanilla(num_classes=10, in_channels=self.in_channels)
            elif self.model_name == 'AlexNet':
                model = AlexNet(num_classes=10, in_channels=self.in_channels)
            elif self.model_name == 'ResNet':
                model = ResNet(num_classes=10, in_dim=self.in_channels)

            model_trainer = CNNTrainTestManager(model=model,
                                                trainset=self.train_set,
                                                testset=self.test_set,
                                                batch_size=self.batch_size,
                                                loss_fn=nn.CrossEntropyLoss(),
                                                optimizer_factory=self.optimizer_factory,
                                                validation=self.val_set,
                                                use_cuda=True,
                                                train_index_list=train_index)
            
            model_trainer.train(self.num_epochs)
            accuracies.append(model_trainer.evaluate_on_test_set())

        self.accuracies = accuracies
    
    def get_accuracies(self):
        return self.accuracies
