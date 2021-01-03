from dataclasses import dataclass
from pathlib import Path

from yaml import YAMLError, safe_load

from constants import CONFIGS_DIRECTORY


@dataclass
class Config:
    batch_size: int
    gamma: float
    eps_start: float
    eps_end: float
    eps_decay: int
    epoch_duration: int
    n_test_runs: int

    @staticmethod
    def from_config_dict(config_dict: dict):
        return Config(
            batch_size=config_dict['batch_size'],
            gamma=config_dict['gamma'],
            epoch_duration=config_dict['epoch_duration'],
            n_test_runs=config_dict['n_test_runs'],
            eps_start=config_dict['eps']['start'],
            eps_end=config_dict['eps']['end'],
            eps_decay=config_dict['eps']['decay']
        )

    @staticmethod
    def default():
        with open(CONFIGS_DIRECTORY / "dqn_config.default.yml", 'r') as f:
            try:
                config_file = safe_load(f)
                return Config.from_config_dict(config_file)
            except YAMLError as exc:
                print("dqn config loading failed. stacktrace:")
                print(exc)

    @staticmethod
    def custom(path: Path):
        with open(path, 'r') as f:
            try:
                config_file = safe_load(f)
                return Config.from_config_dict(config_file)
            except YAMLError as exc:
                print("dqn config loading failed. stacktrace:")
                print(exc)