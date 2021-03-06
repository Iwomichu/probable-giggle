import random
from typing import List

from models.DQN.Transition import Transition


class ReplayMemory:

    def __init__(self, capacity: int):
        self.capacity = capacity
        self.memory: List[Transition] = []
        self.position = 0

    def push(self, *args):
        if len(self.memory) < self.capacity:
            self.memory.append(None)
        self.memory[self.position] = Transition(*args)
        self.position = (self.position + 1) % self.capacity

    def __len__(self):
        return len(self.memory)

    def sample(self, batch_size):
        return random.sample(self.memory, batch_size)
