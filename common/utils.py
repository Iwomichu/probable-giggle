import gym
import torch


device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def process_observation(observation: gym.spaces.Box) -> torch.Tensor:
    """
    Process WxHxC observation box to CxHxW FloatTensor and optionally transfer it to cuda device

    :param observation: Observation to be processed
    :return: Processed observation
    """
    tensor = torch.tensor(observation).transpose(0, 2).to(device)
    if torch.cuda.is_available():
        return tensor.type(torch.cuda.FloatTensor)
    else:
        return tensor.type(torch.FloatTensor)