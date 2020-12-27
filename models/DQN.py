import math
import random
from collections import namedtuple

import gym
import pygame
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from PIL import Image
from opt_einsum.backends import torch
from torch import optim
import torch

from itertools import count
from env import SpaceGameEnvironmentConfig
from env import EnvironmentAction
from env.RewardSystem import RewardSystem
from space_game.ai.AIActionToEventMapping import AIActionToEventMapping
from space_game.Config import Config
from space_game.GameController import GameController
from space_game.Player import create_human_player_1, create_human_player_2
from space_game.events.KeyPressedEvent import KeyPressedEvent
from space_game.events.creation_events.NewEventProcessorAddedEvent import NewEventProcessorAddedEvent
from space_game.events.DamageDealtEvent import DamageDealtEvent
from space_game.events.PlayerAcceleratedEvent import PlayerAcceleratedEvent
from space_game.events.PlayerDestroyedEvent import PlayerDestroyedEvent
from space_game.events.PlayerShootsEvent import PlayerShootsEvent
from space_game.events.creation_events.NewObjectCreatedEvent import NewObjectCreatedEvent
Transition = namedtuple('Transition',
                            ('state', 'action', 'next_state', 'reward'))

def process_map(window) -> np.ndarray:
    array_raw = pygame.surfarray.array3d(window)
    array_processed = np.array(Image.fromarray(array_raw).resize(size=(Config.scaled_height, Config.scaled_width)))
    tensor = torch.tensor(array_processed).transpose(2, 0).unsqueeze(0).to(device)
    if device == "cuda":
        return tensor.type(torch.cuda.FloatTensor)
    else:
        return tensor.type(torch.FloatTensor)

def get_agent_position(agent):
    agent.get_coordinates()

def get_screen(env):
    return process_map(env.config.window)


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



class SGEnv(gym.Env):
    def __init__(self):
        super(SGEnv, self).__init__()
        self.steps_left = 200
        self.running = True
        self.clock = pygame.time.Clock()
        self.config = Config()
        self.game_controller = GameController(self.config)
        self.agent, p1_controller = create_human_player_1(self.config, self.game_controller.event_manager)
        self.reward_system = RewardSystem(self.config, self.agent)
        self.opponent, p2_controller = create_human_player_2(self.config, self.game_controller.event_manager)
        self.game_controller.__add_player__(self.agent, p1_controller)
        self.game_controller.__add_player__(self.opponent, p2_controller)

        self.game_controller.event_manager.add_event(NewObjectCreatedEvent(self.reward_system))
        self.game_controller.event_manager.add_event(
            NewEventProcessorAddedEvent(id(self.reward_system), DamageDealtEvent))

        self.action_space = gym.spaces.Discrete(len(AIActionToEventMapping))
        self.observation_space = gym.spaces.Box(high=0, low=255, shape=(64, 64, 3))

    def reset(self):
        self.game_controller = GameController(self.config)
        self.clock = pygame.time.Clock()
        self.agent, p1_controller = create_human_player_1(self.config, self.game_controller.event_manager)
        self.opponent, p2_controller = create_human_player_2(self.config, self.game_controller.event_manager)
        self.game_controller.__add_player__(self.agent, p1_controller)
        self.game_controller.__add_player__(self.opponent, p2_controller)

        self.game_controller.event_manager.add_event(NewObjectCreatedEvent(self.reward_system))
        self.game_controller.event_manager.add_event(
            NewEventProcessorAddedEvent(id(self.reward_system), DamageDealtEvent))

    def step(self, action: EnvironmentAction):

        self.clock.tick(self.config.fps)
        events = AIActionToEventMapping.get(EnvironmentAction.EnvironmentActionToAIActionMapping.get(action))(id(self.agent))
        for event in events:
            #print(event)
            self.game_controller.event_manager.add_event(event)
        done = self.reward_system.is_game_over()
        reward = self.reward_system.get_reward_and_reset() + SpaceGameEnvironmentConfig.SpaceGameEnvironmentConfig.step_reward
        if (reward>0):
            print(reward)
        self.game_controller.__refresh__()
        if self.steps_left == 0:
            done = True
        self.game_controller.event_manager.process_events()
        info = {"agent_hp": self.agent.hitpoints, "opponent_hp": self.opponent.hitpoints}
        return process_map(self.config.window), reward, done, info




class DQN(nn.Module):
    def __init__(self, weight, height, outputs):
        super(DQN, self).__init__()
        self.conv1 = nn.Conv2d(3, 16, kernel_size=5, stride=2)
        self.bn1 = nn.BatchNorm2d(16)
        self.conv2 = nn.Conv2d(16, 32, kernel_size=5, stride=2)
        self.bn2 = nn.BatchNorm2d(32)
        self.conv3 = nn.Conv2d(32, 32, kernel_size=5, stride=2)
        self.bn3 = nn.BatchNorm2d(32)

        def conv2d_size_out(size, kernel_size=5, stride=2):
            return (size - (kernel_size - 1) - 1) // stride + 1

        convw = conv2d_size_out(conv2d_size_out(conv2d_size_out(weight)))
        convh = conv2d_size_out(conv2d_size_out(conv2d_size_out(height)))
        linear_input_size = convw * convh * 32
        self.head = nn.Linear(linear_input_size, outputs)

    def forward(self, x):
        x = F.relu(self.bn1(self.conv1(x)))
        x = F.relu(self.bn2(self.conv2(x)))
        x = F.relu(self.bn3(self.conv3(x)))
        return self.head(x.view(x.size(0), -1))




if __name__ == "__main__":
    env = SGEnv()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    BATCH_SIZE = 128
    GAMMA = 0.999
    EPS_START = 0.9
    EPS_END = 0.05
    EPS_DECAY = 200
    TARGET_UPDATE = 10

    env = SGEnv()
    init_screen = get_screen(env)
    _, _, screen_height, screen_width = init_screen.shape
    n_actions = env.action_space.n
    policy_net = DQN(screen_height, screen_width, n_actions).to(device)
    target_net = DQN(screen_height, screen_width, n_actions).to(device)
    target_net.load_state_dict(policy_net.state_dict())
    target_net.eval()
    optimizer = optim.RMSprop(policy_net.parameters())

    memory = ReplayMemory(10000)

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

# Training loop
    num_episodes = 200
    for i_episode in range(num_episodes):
        env.reset()
        last_screen = get_screen(env)
        current_screen = get_screen(env)
        state = current_screen - last_screen
        for t in range(2000):
            action = select_action(state)
            _, reward, done, _ = env.step(action.item())
            if reward > 0:
                print(reward)
            reward = torch.tensor([reward], device=device)
            last_screen = current_screen
            current_screen = get_screen(env)
            if not done:
                next_state = current_screen - last_screen
            else:
                next_state = None
            memory.push(state, action, next_state, reward)
            state = next_state
            optimize_model()
            if(t%100 ==0):
                print(t)
            if done:
                break


