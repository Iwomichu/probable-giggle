from pathlib import Path
from typing import Any

import torch

from abc import ABCMeta, abstractmethod


class TorchNNModuleInterface(metaclass=ABCMeta):
    @abstractmethod
    def __init__(self, module: torch.nn.Module):
        self.module = module

    @abstractmethod
    def predict(self, observation: Any) -> Any:
        pass
