import math
import torch
import random
import gym

from pathlib import Path
from typing import Tuple
from torch.nn.functional import smooth_l1_loss
from collections import deque
from torch.optim.optimizer import Optimizer
from torch.optim.rmsprop import RMSprop
from torch.utils.tensorboard.writer import SummaryWriter
from datetime import datetime, timezone

from env import SpaceGameGymAPIEnvironment
from env.EnvironmentAction import EnvironmentAction
from env.SpaceGameEnvironmentConfig import SpaceGameEnvironmentConfig
from models.DQN.Config import Config
from models.DQN.DQN import DQN
from models.DQN.ReplayMemory import ReplayMemory
from game_recorder.GameRecorder import GameRecorder
from constants import RECORDED_GAMES_DIRECTORY, TRAINING_LOGS_DIRECTORY
from models.DQN.Transition import Transition
from models.DQN.domain_types import HasAgentWon, GameLength, ProcessedObservation, RawAction, State

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def process_observation(observation: gym.spaces.Box) -> ProcessedObservation:
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


def train(
        env: SpaceGameGymAPIEnvironment = None,
        dqn_config: Config = None,
        custom_logs_directory: Path = None,
        custom_recordings_directory: Path = None
) -> DQN:
    train_run_id = f"CustomDQN_{datetime.now(tz=timezone.utc).strftime('%H-%M-%S_%d-%m-%Y')}"
    recordings_directory = custom_recordings_directory \
        if custom_recordings_directory is not None \
        else RECORDED_GAMES_DIRECTORY / train_run_id
    logs_directory = custom_logs_directory \
        if custom_logs_directory is not None \
        else TRAINING_LOGS_DIRECTORY / train_run_id
    writer = SummaryWriter(log_dir=logs_directory)

    dqn_config = dqn_config if dqn_config is not None else Config.default()

    if env is None:
        env_config = SpaceGameEnvironmentConfig.default()
        env = SpaceGameGymAPIEnvironment.SpaceGameEnvironment(env_config)

    random_screen = process_observation(env.observation_space.sample())
    _, screen_height, screen_width = random_screen.shape
    n_actions = env.action_space.n
    policy_net = DQN(screen_height, screen_width, n_actions).to(device)
    target_net = DQN(screen_height, screen_width, n_actions).to(device)
    target_net.load_state_dict(policy_net.state_dict())
    target_net.eval()
    optimizer = RMSprop(policy_net.parameters())

    memory = ReplayMemory(dqn_config.memory_size)

    steps_done = 0

    # Training loop
    test_episode_count = 0
    for i_episode in range(dqn_config.games_total):
        observation = env.reset()
        last_screen = process_observation(observation)
        current_screen = process_observation(observation)
        last_frame = current_screen - last_screen if dqn_config.is_state_based_on_change else last_screen
        cumulative_reward = 0.
        history = deque([last_frame])
        for _ in range(2):
            observation, _, _, _ = env.step(EnvironmentAction.StandStill)
            last_screen = current_screen
            current_screen = process_observation(observation)
            last_frame = current_screen - last_screen if dqn_config.is_state_based_on_change else last_screen
            history.append(last_frame)
        state = torch.cat(tuple(history)).unsqueeze(0)
        for t in range(3000):
            action = select_action(
                dqn_config.eps_end, dqn_config.eps_start, dqn_config.eps_decay, policy_net, n_actions, state, steps_done
            )
            action_parsed = EnvironmentAction(action.item())
            steps_done += 1
            observation, reward, done, info = env.step(action_parsed)
            cumulative_reward += reward
            reward = torch.tensor([reward], device=device)
            last_screen = current_screen
            current_screen = process_observation(observation)
            if not done:
                next_frame = current_screen - last_screen if dqn_config.is_state_based_on_change else last_screen
                # ':' at first index since it is squeeze dummy dimension
                next_state = torch.cat((state[:, 1:, :, :], next_frame.unsqueeze(0)), dim=1)
            else:
                next_state = None
            memory.push(state, action, next_state, reward)
            state = next_state
            optimize_model(memory, dqn_config.batch_size, policy_net, target_net, dqn_config.gamma, optimizer)
            if done:
                print(f"Episode {i_episode}")
                print(info)
                break

        if (i_episode + 1) % dqn_config.target_update == 0:
            target_net.load_state_dict(policy_net.state_dict())

        writer.add_scalar("Episode reward", cumulative_reward, i_episode)

        # Testing phase
        if (i_episode+1) % dqn_config.epoch_duration == 0:
            with torch.no_grad():
                games_won_lengths = []
                games_lost_lengths = []
                for i_test_run in range(dqn_config.n_test_runs):
                    game_length, has_won = test_game(env, recordings_directory, test_episode_count, target_net,
                                                     i_test_run, dqn_config)
                    if has_won:
                        games_won_lengths.append(game_length)
                    else:
                        games_lost_lengths.append(game_length)
                win_ratio = len(games_won_lengths) / dqn_config.n_test_runs
                if games_won_lengths:
                    won_game_average_length = sum(games_won_lengths)/len(games_won_lengths)
                else:
                    won_game_average_length = 0
                if games_lost_lengths:
                    lost_game_average_length = sum(games_lost_lengths)/len(games_lost_lengths)
                else:
                    lost_game_average_length = 0
                game_average_length = sum(games_won_lengths+games_lost_lengths) / dqn_config.n_test_runs
                writer.add_scalar("Test episode win ratio", win_ratio, test_episode_count)
                writer.add_scalar("Test episode won game average length", won_game_average_length, test_episode_count)
                writer.add_scalar("Test episode lost game average length", lost_game_average_length, test_episode_count)
                writer.add_scalar("Test episode game average length", game_average_length, test_episode_count)
                print("======================")
                print(f"Test episode {test_episode_count} stats: ")
                print("======================")
                print(f"win_ratio: {win_ratio}")
                print(f"won_game_average_length: {won_game_average_length}")
                print(f"lost_game_average_length: {lost_game_average_length}")
                print(f"game_average_length: {game_average_length}")
                print("======================")
                test_episode_count += 1

    print("STOP")
    return target_net


def select_action(
        eps_done: float, eps_start: float, eps_decay: int, policy_net: DQN,
        n_actions: int, state: State, steps_done: int
) -> RawAction:
    sample = random.random()
    eps_threshold = eps_done + (eps_start - eps_done) * math.exp(-1. * steps_done / eps_decay)
    if sample > eps_threshold:
        with torch.no_grad():
            return policy_net(state).max(1)[1].view(1, 1)
    else:
        return torch.tensor([[random.randrange(n_actions)]], device=device, dtype=torch.long)


def optimize_model(
        memory: ReplayMemory, batch_size: int,
        policy_net: DQN, target_net: DQN, gamma: float, optimizer: Optimizer
) -> None:
    if len(memory) < batch_size:
        return
    transitions = memory.sample(batch_size)
    batch = Transition(*zip(*transitions))
    non_final_mask = torch.tensor(tuple(map(lambda s: s is not None,
                                            batch.next_state)), device=device, dtype=torch.bool)

    non_final_next_states = torch.cat([s for s in batch.next_state
                                       if s is not None])
    state_batch = torch.cat(batch.state)
    action_batch = torch.cat(batch.action)
    reward_batch = torch.cat(batch.reward)

    state_action_values = policy_net(state_batch).gather(1, action_batch)
    next_state_values = torch.zeros(batch_size, device=device)
    next_state_values[non_final_mask] = target_net(non_final_next_states).max(1)[0].detach()
    expected_state_action_values = (next_state_values * gamma) + reward_batch

    loss = smooth_l1_loss(state_action_values, expected_state_action_values.unsqueeze(1))

    optimizer.zero_grad()
    loss.backward()
    for param in policy_net.parameters():
        param.grad.data.clamp_(-1, 1)
    optimizer.step()


def test_game(
        env: gym.Env, recordings_directory: Path, test_episode_count: int,
        policy_net: DQN, run_id: int, dqn_config: Config
) -> Tuple[GameLength, HasAgentWon]:
    screen_raw = env.reset()
    last_screen = process_observation(screen_raw)
    current_screen = last_screen
    raw_screen_width, raw_screen_height, _ = screen_raw.shape
    done = False
    game_length = 0
    info = {'agent_hp': float('inf')}
    last_frame = current_screen - last_screen
    _, pov_screen_width, pov_screen_height = last_frame.shape
    history = deque([last_frame])
    recorder = GameRecorder(
        raw_screen_width,
        raw_screen_height,
        grayscale=True,
        directory_path=recordings_directory,
        filename=f"{test_episode_count}_{run_id}_raw"
    )
    recorder_pov = GameRecorder(
        pov_screen_width,
        pov_screen_height,
        grayscale=True,
        directory_path=recordings_directory,
        filename=f"{test_episode_count}_{run_id}_pov"
    )
    for _ in range(2):
        observation, _, _, _ = env.step(0)
        last_screen = current_screen
        current_screen = process_observation(observation)
        recorder.add_torch_frame(current_screen.cpu())
        last_frame = current_screen - last_screen if dqn_config.is_state_based_on_change else last_screen
        recorder_pov.add_torch_frame(last_frame.cpu())
        history.append(last_frame)
    state = torch.cat(tuple(history)).unsqueeze(0)
    while not done:
        action = policy_net(state).max(1)[1].view(1, 1)
        observation, _, done, info = env.step(action.item())
        last_screen = current_screen
        current_screen = process_observation(observation)
        recorder.add_torch_frame(current_screen.cpu())
        next_frame = current_screen - last_screen if dqn_config.is_state_based_on_change else last_screen
        recorder_pov.add_torch_frame(next_frame.cpu())
        state = torch.cat((state[:, 1:, :, :], next_frame.unsqueeze(0)), dim=1)
        game_length += 1
    recorder.save_recording()
    recorder_pov.save_recording()
    return game_length, info['agent_hp'] > 0


if __name__ == "__main__":
    train()
