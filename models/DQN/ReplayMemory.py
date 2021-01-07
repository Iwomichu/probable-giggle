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
        self.position += 1
        self.position = self.position % self.capacity

    def __len__(self):
        return len(self.memory)

    def sample(self, batch_size, device):
        s = random.sample(self.memory, batch_size)
        return [Transition(state.to(device), action, next_state.to(device) if next_state is not None else None, reward)
                for state, action, next_state, reward in s]
