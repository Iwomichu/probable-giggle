import gym
import torch


def process_observation(observation: gym.spaces.Box) -> torch.Tensor:
    """
    Process WxHxC observation box to CxHxW FloatTensor and optionally transfer it to cuda device

    :param observation: Observation to be processed
    :return: Processed observation
    """
    return torch.tensor(observation).transpose(0, 2)
