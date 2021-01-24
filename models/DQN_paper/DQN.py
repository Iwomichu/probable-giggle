import torch
from torch import nn as nn
from torch.nn import functional as F


class DQN(nn.Module):
    def __init__(self, width, height, outputs):
        super(DQN, self).__init__()
        self.conv1 = nn.Conv2d(3, 16, kernel_size=8, stride=4)
        self.conv2 = nn.Conv2d(16, 32, kernel_size=4, stride=2)

        def conv2d_size_out(size, kernel_size=5, stride=2):
            return (size - (kernel_size - 1) - 1) // stride + 1

        convw = conv2d_size_out(conv2d_size_out(width, kernel_size=8, stride=4), kernel_size=4, stride=2)
        convh = conv2d_size_out(conv2d_size_out(height, kernel_size=8, stride=4), kernel_size=4, stride=2)
        linear_input_size = convw * convh * 32
        self.l1 = nn.Linear(linear_input_size, 256)
        self.head = nn.Linear(256, outputs)

    def forward(self, x: torch.IntTensor):
        x = F.relu(self.conv1(x))
        x = F.relu(self.conv2(x))
        x = F.relu(self.l1(x.view(x.size()[0], -1)))
        return self.head(x)
