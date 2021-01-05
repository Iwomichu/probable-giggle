from pathlib import Path

import gym
import torch

from env.EnvironmentAction import EnvironmentAction
from common.TorchNNModuleInterface import TorchNNModuleInterface
from common.utils import process_observation


class DQNWrapper(TorchNNModuleInterface):
    def __init__(self, module: torch.nn.Module):
        super(DQNWrapper, self).__init__(module)
        self.module = module
        self.state = torch.zeros((1, 3, 64, 64))

    def predict(self, observation: gym.spaces.Box) -> EnvironmentAction:
        processed_observation = process_observation(observation)
        self.state = torch.cat((self.state[:, 1:, :, :], processed_observation.unsqueeze(0)), dim=1)
        raw_action = self.module(self.state).max(1)[1].view(1, 1)
        return EnvironmentAction(raw_action.item())

    @staticmethod
    def from_file(path: Path):
        model = torch.load(str(path))
        return DQNWrapper(model)
