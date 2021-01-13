import math
import torch
import random
import numpy as np

from pathlib import Path
from typing import Tuple
from torch.optim.optimizer import Optimizer
from torch.optim.rmsprop import RMSprop
from torch.utils.tensorboard.writer import SummaryWriter
from datetime import datetime, timezone
from copy import deepcopy

from env.SpaceGameGymAPIEnvironment import SpaceGameEnvironment
from env.SpaceGameSelfPlayEnvironment import SpaceGameSelfPlayEnvironment
from env.EnvironmentAction import EnvironmentAction
from env.SpaceGameEnvironmentConfig import SpaceGameEnvironmentConfig
from models.DQN.Config import Config
from models.DQN.DQN import DQN
from models.DQN.ReplayMemory import ReplayMemory
from models.DQN.single_agent_training import optimize_model
from game_recorder.GameRecorder import GameRecorder
from constants import RECORDED_GAMES_DIRECTORY, TRAINING_LOGS_DIRECTORY, SAVED_MODELS_DIRECTORY
from models.DQN.domain_types import HasAgentWon, GameLength, ProcessedObservation, RawAction, State

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def process_observation_self_play(observation: np.array) -> ProcessedObservation:
    """
    Process WxHxC observation box to CxHxW FloatTensor and optionally transfer it to cuda device

    :param observation: Observation to be processed
    :return: Processed observation
    """
    return torch.tensor(observation.copy()).transpose(0, 2)


def prepare_model(screen_height: int, screen_width: int,
                  n_actions: int, old_model: DQN = None) -> Tuple[DQN, DQN, Optimizer]:
    policy_net = DQN(screen_height, screen_width, n_actions).to(device)
    target_net = DQN(screen_height, screen_width, n_actions).to(device)
    if old_model is not None:
        policy_net.load_state_dict(old_model.state_dict())
    target_net.load_state_dict(policy_net.state_dict())
    target_net.eval()
    optimizer = RMSprop(policy_net.parameters())
    return policy_net, target_net, optimizer


def train_model(
        env: SpaceGameSelfPlayEnvironment = None,
        dqn_config: Config = None,
        custom_logs_directory: Path = None,
        custom_recordings_directory: Path = None,
        visualize_test: bool = False,
        old_model: DQN = None
) -> Tuple[DQN, DQN]:
    train_run_id = f"CustomDQN_{datetime.now(tz=timezone.utc).strftime('%H-%M-%S_%d-%m-%Y')}"
    recordings_directory = custom_recordings_directory \
        if custom_recordings_directory is not None \
        else RECORDED_GAMES_DIRECTORY / train_run_id
    logs_directory = custom_logs_directory \
        if custom_logs_directory is not None \
        else TRAINING_LOGS_DIRECTORY / train_run_id
    model_save_directory = SAVED_MODELS_DIRECTORY / train_run_id
    model_save_directory.mkdir(parents=True, exist_ok=True)
    writer = SummaryWriter(log_dir=logs_directory)

    dqn_config = dqn_config if dqn_config is not None else Config.default()

    if env is None:
        env_config = SpaceGameEnvironmentConfig.default()
        env = SpaceGameSelfPlayEnvironment(env_config)

    random_screen = process_observation_self_play(env.sample_observation_space())
    _, screen_height, screen_width = random_screen.shape
    n_actions = env.get_n_actions()

    policy_net_up, target_net_up, optimizer_up = prepare_model(screen_height, screen_width, n_actions, old_model)
    policy_net_down, target_net_down, optimizer_down = prepare_model(screen_height, screen_width, n_actions, old_model)

    memory = ReplayMemory(dqn_config.memory_size)

    steps_done = 0
    test_episode_count = 0
    # Training loop
    for i_episode in range(dqn_config.games_total):
        steps_done = train(
            env, n_actions, policy_net_up, target_net_up,
            policy_net_down, target_net_down,
            memory, optimizer_up, optimizer_down, dqn_config,
            i_episode, recordings_directory, steps_done
        )
        if (i_episode + 1) % dqn_config.target_update == 0:
            target_net_up.load_state_dict(policy_net_up.state_dict())
            target_net_down.load_state_dict(policy_net_down.state_dict())
            torch.save(target_net_up, model_save_directory / "dqn_up.pt")
            torch.save(target_net_down, model_save_directory / "dqn_down.pt")

        if (i_episode + 1) % dqn_config.epoch_duration == 0:
            test(
                test_episode_count, env, dqn_config,
                target_net_up, target_net_down,
                recordings_directory, visualize_test, writer
            )
            test_episode_count += 1

    print("STOP")
    return target_net_up, target_net_down


def select_action(
        eps_done: float, eps_start: float, eps_decay: int, policy_net: DQN,
        n_actions: int, state: State, steps_done: int
) -> RawAction:
    sample = random.random()
    eps_threshold = eps_done + (eps_start - eps_done) * math.exp(-1. * steps_done / eps_decay)
    if sample > eps_threshold:
        with torch.no_grad():
            return policy_net(state.to(device).float()).max(1)[1].view(1, 1)
    else:
        return torch.tensor([[random.randrange(n_actions)]], device=device, dtype=torch.long)


def process_state_change(previous_state: State, raw_observation: np.ndarray,
                         target_net: DQN, policy_net: DQN, memory: ReplayMemory,
                         action_raw: torch.Tensor, reward: float, done: bool,
                         recorder: GameRecorder, dqn_config: Config, optimizer: Optimizer) -> State:
    reward_up = torch.tensor([reward], device=device)
    current_screen = process_observation_self_play(raw_observation)
    if recorder:
        recorder.add_torch_frame(current_screen)
    if not done:
        next_frame = current_screen
        # ':' at first index since it is squeeze dummy dimension
        next_state = torch.cat((previous_state[:, 1:, :, :].data, next_frame.unsqueeze(0)), dim=1)
    else:
        next_state = None
    memory.push(previous_state, action_raw, next_state, reward_up)
    state = next_state
    optimize_model(memory, dqn_config.batch_size, policy_net, target_net, dqn_config.gamma, optimizer)
    return state


def prepare_initial_state(env: SpaceGameEnvironment) -> State:
    observation_up = env.reset()
    processed_screen_up = process_observation_self_play(
        observation_up)
    history_up = [processed_screen_up]
    for _ in range(2):
        observation_up, _, _, _ = env.step(EnvironmentAction.StandStill)
        processed_screen_up = process_observation_self_play(observation_up)
        history_up.append(processed_screen_up)
    state_up = torch.cat(tuple(history_up)).unsqueeze(0)
    return state_up


def prepare_initial_states(env: SpaceGameSelfPlayEnvironment, steps_done: int) -> Tuple[State, State]:
    observation_up, observation_down = env.reset(steps_done)
    processed_screen_up, processed_screen_down = process_observation_self_play(
        observation_up), process_observation_self_play(observation_down)
    history_up = [processed_screen_up]
    history_down = [processed_screen_down]
    for _ in range(2):
        (_, observation_up, _), (_, observation_down, _) = env.step(
            (EnvironmentAction.StandStill, EnvironmentAction.StandStill)
        )
        processed_screen_up = process_observation_self_play(observation_up)
        history_up.append(processed_screen_up)
        processed_screen_down = process_observation_self_play(observation_down)
        history_down.append(processed_screen_down)
    state_up = torch.cat(tuple(history_up)).unsqueeze(0)
    state_down = torch.cat(tuple(history_down)).unsqueeze(0)
    return state_up, state_down


def train(
        env: SpaceGameSelfPlayEnvironment,
        n_actions: int,
        policy_net_up: DQN,
        target_net_up: DQN,
        policy_net_down: DQN,
        target_net_down: DQN,
        memory: ReplayMemory,
        optimizer_up: Optimizer,
        optimizer_down: Optimizer,
        dqn_config: Config,
        i_episode: int,
        recordings_directory: Path,
        steps_done: int
) -> int:
    up_recorder = None
    down_recorder = None
    recordable_game = ((i_episode + 1) % dqn_config.target_update) == 0
    if recordable_game:
        screen_width, screen_height, _ = env.sample_observation_space().shape
        up_recorder = GameRecorder(
            screen_width,
            screen_height,
            grayscale=True,
            directory_path=recordings_directory,
            filename=f"up_{i_episode}_raw"
        )
        down_recorder = GameRecorder(
            screen_width,
            screen_height,
            grayscale=True,
            directory_path=recordings_directory,
            filename=f"down_{i_episode}_raw"
        )
    state_up, state_down = prepare_initial_states(env, steps_done)
    for t in range(3000):
        action_up = select_action(
            dqn_config.eps_end, dqn_config.eps_start, dqn_config.eps_decay, policy_net_up, n_actions,
            state_up.to(device), steps_done
        )
        action_down = select_action(
            dqn_config.eps_end, dqn_config.eps_start, dqn_config.eps_decay, policy_net_down, n_actions,
            state_down.to(device), steps_done
        )
        action_parsed_up = EnvironmentAction(action_up.item())
        action_parsed_down = EnvironmentAction(action_down.item())
        steps_done += 1
        (reward_up, observation_up, done_up), (reward_down, observation_down, done_down) = env.step(
            (action_parsed_up, action_parsed_down)
        )
        state_up = process_state_change(
            state_up, observation_up, target_net_up, target_net_up, memory, action_up, reward_up,
            done_up or done_down, up_recorder, dqn_config, optimizer_up
        )
        state_down = process_state_change(
            state_down, observation_down, target_net_down, target_net_down, memory, action_down, reward_down,
            done_up or done_down, down_recorder, dqn_config, optimizer_down
        )
        if done_up or done_down:
            print(f"Episode {i_episode}")
            if up_recorder:
                up_recorder.save_recording()
            if down_recorder:
                down_recorder.save_recording()
            break
    return steps_done


def test(
        test_episode_count: int,
        env: SpaceGameSelfPlayEnvironment,
        dqn_config: Config,
        target_net_up: DQN,
        target_net_down: DQN,
        recordings_directory: Path,
        visualize_test: bool,
        writer: SummaryWriter
):
    print("test_episode: ", test_episode_count)
    env_config_copied = deepcopy(env.environment_config)
    env_config_copied.render = visualize_test
    game_config_copied = deepcopy(env.space_game_config)
    test_env = SpaceGameEnvironment(game_config=game_config_copied, environment_config=env_config_copied)
    win_rate_up, average_game_duration_up = test_model(test_env, dqn_config, target_net_up,
                                                       recordings_directory, test_episode_count)
    win_rate_down, average_game_duration_down = test_model(test_env, dqn_config, target_net_down,
                                                           recordings_directory, test_episode_count)
    writer.add_scalar("Test episode upside winratio", win_rate_up, test_episode_count)
    writer.add_scalar("Test episode upside average game length", average_game_duration_up,
                      test_episode_count)
    print("upside win ratio: ", win_rate_up)
    print("upside game length: ", average_game_duration_up)
    writer.add_scalar("Test episode upside winratio", win_rate_down, test_episode_count)
    writer.add_scalar("Test episode upside average game length", average_game_duration_down,
                      test_episode_count)
    print("upside win ratio: ", win_rate_down)
    print("upside game length: ", average_game_duration_down)


def test_model(test_env: SpaceGameEnvironment, dqn_config: Config, policy_net: DQN,
               recordings_directory: Path, test_episode_count: int) -> Tuple[int, float]:
    won_games = 0
    game_durations = 0
    with torch.no_grad():
        for run_id in range(dqn_config.n_test_runs):
            game_duration, has_won = test_game(env=test_env, policy_net=policy_net,
                                               test_episode_count=test_episode_count,
                                               recordings_directory=recordings_directory, run_id=f"{run_id}_up")
            won_games += (1 if has_won else 0)
            game_durations += game_duration
    return won_games // dqn_config.n_test_runs, game_durations / dqn_config.n_test_runs


def test_game(
        env: SpaceGameEnvironment, recordings_directory: Path, test_episode_count: int,
        policy_net: DQN, run_id: str
) -> Tuple[GameLength, HasAgentWon]:
    done = False
    game_length = 0
    info = {'agent_hp': float('inf')}
    raw_screen_width, raw_screen_height, _ = env.sample_observation_space().shape
    pov_screen_width, pov_screen_height = raw_screen_width, raw_screen_height
    recorder = GameRecorder(
        raw_screen_width,
        raw_screen_height,
        grayscale=True,
        directory_path=recordings_directory,
        filename=f"test_{test_episode_count}_{run_id}_raw"
    )
    recorder_pov = GameRecorder(
        pov_screen_width,
        pov_screen_height,
        grayscale=True,
        directory_path=recordings_directory,
        filename=f"test_{test_episode_count}_{run_id}_pov"
    )

    state = prepare_initial_state(env)
    while not done:
        action = policy_net(state.to(device).float()).max(1)[1].view(1, 1)
        observation, _, done, info = env.step(action.item())
        current_screen = process_observation_self_play(observation)
        recorder.add_torch_frame(current_screen)
        next_frame = current_screen
        recorder_pov.add_torch_frame(next_frame)
        state = torch.cat((state[:, 1:, :, :], next_frame.unsqueeze(0)), dim=1)
        game_length += 1
    recorder.save_recording()
    recorder_pov.save_recording()
    return game_length, info['agent_hp'] > 0


if __name__ == "__main__":
    train_model()
