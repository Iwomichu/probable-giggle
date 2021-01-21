from typing import Union

import torch

HasAgentWon = bool
GameLength = int
ProcessedObservation = Union[torch.FloatTensor, torch.cuda.FloatTensor]
RawAction = torch.Tensor  # 0-dimensional Tensor representing action selected by DQN
State = torch.Tensor  # NxCxHxW Tensor representing N consecutive ProcessedObservations
Reward = float
