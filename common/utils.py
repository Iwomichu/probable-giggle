import gym
import torch

from space_game.ai.AIAction import AIAction


def process_observation(observation: gym.spaces.Box) -> torch.Tensor:
    """
    Process WxHxC observation box to CxHxW FloatTensor and optionally transfer it to cuda device

    :param observation: Observation to be processed
    :return: Processed observation
    """
    return torch.from_numpy(observation).transpose(0, 2)


def inverse_movement(action: AIAction) -> AIAction:
    """
    Inverses action along X axis (UP <-> DOWN)

    :param action: Original action
    :return: Inversed action (UP = DOWN)
    """
    inversion_dict = {
        AIAction.MoveDown: AIAction.MoveUp,
        AIAction.MoveDownShoot: AIAction.MoveUpShoot,
        AIAction.MoveLeftDown: AIAction.MoveLeftUp,
        AIAction.MoveLeftDownShoot: AIAction.MoveLeftUpShoot,
        AIAction.MoveRightDown: AIAction.MoveRightUp,
        AIAction.MoveRightDownShoot: AIAction.MoveRightUpShoot,
        AIAction.MoveUp: AIAction.MoveDown,
        AIAction.MoveUpShoot: AIAction.MoveDownShoot,
        AIAction.MoveLeftUp: AIAction.MoveLeftDown,
        AIAction.MoveLeftUpShoot: AIAction.MoveLeftDownShoot,
        AIAction.MoveRightUp: AIAction.MoveRightDown,
        AIAction.MoveRightUpShoot: AIAction.MoveRightDownShoot
    }
    return inversion_dict.get(action) if action in inversion_dict else action
