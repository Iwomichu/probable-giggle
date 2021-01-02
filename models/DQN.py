import math
from typing import Tuple

import torch
import random
import gym
import torch.nn as nn
import torch.nn.functional as F
from collections import namedtuple, deque
from torch import optim
from torch.utils.tensorboard.writer import SummaryWriter
from datetime import datetime, timezone

from env import SpaceGameGymAPIEnvironment
from env.SpaceGameEnvironmentConfig import SpaceGameEnvironmentConfig
from space_game.ai.DecisionBasedController import DecisionBasedController
from game_recorder.GameRecorder import GameRecorder
from constants import RECORDED_GAMES_DIRECTORY, TRAINING_LOGS_DIRECTORY

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
Transition = namedtuple('Transition', ('state', 'action', 'next_state', 'reward'))
HasAgentWon = bool
GameLength = int


def process_observation(observation: gym.spaces.Box) -> torch.Tensor:
    tensor = torch.tensor(observation).transpose(0, 2).to(device)
    if torch.cuda.is_available():
        return tensor.type(torch.cuda.FloatTensor)
    else:
        return tensor.type(torch.FloatTensor)


class ReplayMemory(object):

    def __init__(self, capacity):
        self.capacity = capacity
        self.memory = []
        self.position = 0

    def push(self, *args):
        if len(self.memory) < self.capacity:
            self.memory.append(None)
        self.memory[self.position] = Transition(*args)
        self.position += 1
        self.position = self.position % self.capacity

    def __len__(self):
        return len(self.memory)

    def sample(self, batch_size):
        return random.sample(self.memory, batch_size)


class DQN(nn.Module):
    def __init__(self, width, height, outputs):
        super(DQN, self).__init__()
        self.conv1 = nn.Conv2d(3, 16, kernel_size=5, stride=2)
        self.bn1 = nn.BatchNorm2d(16)
        self.conv2 = nn.Conv2d(16, 32, kernel_size=5, stride=2)
        self.bn2 = nn.BatchNorm2d(32)
        self.conv3 = nn.Conv2d(32, 32, kernel_size=5, stride=2)
        self.bn3 = nn.BatchNorm2d(32)

        def conv2d_size_out(size, kernel_size=5, stride=2):
            return (size - (kernel_size - 1) - 1) // stride + 1

        convw = conv2d_size_out(conv2d_size_out(conv2d_size_out(width)))
        convh = conv2d_size_out(conv2d_size_out(conv2d_size_out(height)))
        linear_input_size = convw * convh * 32
        self.head = nn.Linear(linear_input_size, outputs)

    def forward(self, x: torch.IntTensor):
        x = F.relu(self.bn1(self.conv1(x)))
        x = F.relu(self.bn2(self.conv2(x)))
        x = F.relu(self.bn3(self.conv3(x)))
        return self.head(x.view(x.size()[0], -1))


def main():

    train_run_id = f"CustomDQN_{datetime.now(tz=timezone.utc).strftime('%H-%M-%S_%d-%m-%Y')}"
    logs_directory = TRAINING_LOGS_DIRECTORY / train_run_id
    recordings_directory = RECORDED_GAMES_DIRECTORY / train_run_id
    writer = SummaryWriter(log_dir=logs_directory)

    BATCH_SIZE = 128
    GAMMA = 0.999
    EPS_START = 0.9
    EPS_END = 0.05
    EPS_DECAY = 200
    TARGET_UPDATE = 10
    N_TEST_RUNS = 20
    env_config = SpaceGameEnvironmentConfig(
        render=False,
        OpponentControllerType=DecisionBasedController,
        step_reward=-.01,
        target_hit_reward=10,
        taken_damage_reward=-10,
        shot_fired_reward=-10
    )
    env = SpaceGameGymAPIEnvironment.SpaceGameEnvironment(env_config)
    random_screen = process_observation(env.observation_space.sample())
    _, screen_height, screen_width = random_screen.shape
    n_actions = env.action_space.n
    policy_net = DQN(screen_height, screen_width, n_actions).to(device)
    target_net = DQN(screen_height, screen_width, n_actions).to(device)
    target_net.load_state_dict(policy_net.state_dict())
    target_net.eval()
    optimizer = optim.RMSprop(policy_net.parameters())

    memory = ReplayMemory(10000)

    global steps_done
    steps_done = 0

    def select_action(state):
        global steps_done
        sample = random.random()
        eps_threshold = EPS_END + (EPS_START - EPS_END) * math.exp(-1. * steps_done / EPS_DECAY)
        steps_done += 1
        if sample > eps_threshold:
            with torch.no_grad():
                return policy_net(state).max(1)[1].view(1, 1)
        else:
            return torch.tensor([[random.randrange(n_actions)]], device=device, dtype=torch.long)

    def optimize_model():
        if len(memory) < BATCH_SIZE:
            return
        transitions = memory.sample(BATCH_SIZE)
        batch = Transition(*zip(*transitions))
        non_final_mask = torch.tensor(tuple(map(lambda s: s is not None,
                                                batch.next_state)), device=device, dtype=torch.bool)

        non_final_next_states = torch.cat([s for s in batch.next_state
                                           if s is not None])
        state_batch = torch.cat(batch.state)
        action_batch = torch.cat(batch.action)
        reward_batch = torch.cat(batch.reward)

        state_action_values = policy_net(state_batch).gather(1, action_batch)
        next_state_values = torch.zeros(BATCH_SIZE, device=device)
        next_state_values[non_final_mask] = target_net(non_final_next_states).max(1)[0].detach()
        expected_state_action_values = (next_state_values * GAMMA) + reward_batch

        loss = F.smooth_l1_loss(state_action_values, expected_state_action_values.unsqueeze(1))

        optimizer.zero_grad()
        loss.backward()
        for param in policy_net.parameters():
            param.grad.data.clamp_(-1, 1)
        optimizer.step()

    def test_run(run_id: int) -> Tuple[GameLength, HasAgentWon]:
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
            directory=recordings_directory,
            filename=f"{test_episode_count}_{run_id}_raw"
        )
        recorder_pov = GameRecorder(
            pov_screen_width,
            pov_screen_height,
            grayscale=True,
            directory=recordings_directory,
            filename=f"{test_episode_count}_{run_id}_pov"
        )
        for _ in range(2):
            observation, _, _, _ = env.step(0)
            last_screen = current_screen
            current_screen = process_observation(observation)
            recorder.add_torch_frame(current_screen)
            last_frame = current_screen - last_screen
            recorder_pov.add_torch_frame(last_frame)
            history.append(last_frame)
        state = torch.cat(tuple(history)).unsqueeze(0)
        while not done:
            action = policy_net(state).max(1)[1].view(1, 1)
            observation, _, done, info = env.step(action.item())
            last_screen = current_screen
            current_screen = process_observation(observation)
            recorder.add_torch_frame(current_screen)
            next_frame = current_screen - last_screen
            recorder_pov.add_torch_frame(next_frame)
            state = torch.cat((state[:, 1:, :, :], next_frame.unsqueeze(0)), dim=1)
            game_length += 1
        recorder.save_recording()
        recorder_pov.save_recording()
        return game_length, info['agent_hp'] > 0

    # Training loop
    num_episodes = 1000
    test_episode_count = 0
    for i_episode in range(num_episodes):
        observation = env.reset()
        last_screen = process_observation(observation)
        current_screen = process_observation(observation)
        last_frame = current_screen - last_screen
        cumulative_reward = 0.
        history = deque([last_frame])
        for _ in range(2):
            observation, _, _, _ = env.step(0)
            last_screen = current_screen
            current_screen = process_observation(observation)
            last_frame = current_screen - last_screen
            history.append(last_frame)
        state = torch.cat(tuple(history)).unsqueeze(0)
        for t in range(3000):
            action = select_action(state)
            observation, reward, done, info = env.step(action.item())
            cumulative_reward += reward
            reward = torch.tensor([reward], device=device)
            last_screen = current_screen
            current_screen = process_observation(observation)
            if not done:
                next_frame = current_screen - last_screen
                next_state = torch.cat((state[:, 1:, :, :], next_frame.unsqueeze(0)), dim=1)  # ':' at first index since it is squeeze dummy dimension
            else:
                next_state = None
            memory.push(state, action, next_state, reward)
            state = next_state
            optimize_model()
            if done:
                print(f"Episode {i_episode}")
                print(info)
                break

        writer.add_scalar("Episode reward", cumulative_reward, i_episode)
        # every 50 episodes conduct 10 test games (games with no learning)
        # test log should contain:
        # * win ratio
        # * average game length
        # * average won game length
        # * average lost game length
        # * video of each game (this needs to be presented outside of TensorBoard)
        if (i_episode+1) % 100 == 0:
            with torch.no_grad():
                games_won_lengths = []
                games_lost_lengths = []
                for i_test_run in range(N_TEST_RUNS):
                    game_length, has_won = test_run(i_test_run)
                    if has_won:
                        games_won_lengths.append(game_length)
                    else:
                        games_lost_lengths.append(game_length)
                win_ratio = len(games_won_lengths)/N_TEST_RUNS
                if games_won_lengths:
                    won_game_average_length = sum(games_won_lengths)/len(games_won_lengths)
                else:
                    won_game_average_length = 0
                if games_lost_lengths:
                    lost_game_average_length = sum(games_lost_lengths)/len(games_lost_lengths)
                else:
                    lost_game_average_length = 0
                game_average_length = sum(games_won_lengths+games_lost_lengths)/N_TEST_RUNS
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


if __name__ == "__main__":
    main()
