import pygame
import numpy
import os
import logging
from dataclasses import dataclass
from collections import defaultdict, namedtuple
from enum import Enum, auto
from typing import Dict, Tuple, List, Set

logger = logging.getLogger()
pygame.init()

KeyId = int
Coordinate = float
Constraint = namedtuple('Constraint', ['min', 'max'])
Acceleration = float
HitPoint = int


class GameController:
    pass


@dataclass()
class Config():
    width = 800
    height = 600
    player_1_width_constraint = Constraint(0, width)
    player_1_height_constraint = Constraint(50, height/2)
    player_2_width_constraint = Constraint(0, width)
    player_2_height_constraint = Constraint(height/2, height - 50)
    player_1_color = [255, 0, 0]
    player_2_color = [0, 0, 255]
    player_1_bullet_color = [255, 127, 0]
    player_2_bullet_color = [127, 0, 255]
    bullet_width = 5
    bullet_height = 10
    shoot_cooldown = 10
    ammo_maximum = 10
    ammo_countdown = 40
    max_acceleration = 8.
    bullet_velocity = 10.
    window = pygame.display.set_mode((width, height))
    fps = 60
    font = pygame.font.SysFont("arial", 20)


@dataclass()
class Assets:
    pass
    #ship_1 = pygame.image.load(os.path.join("assets", "ship_green.png"))


@dataclass()
class Entity:
    x: Coordinate
    y: Coordinate
    sprite: pygame.Surface
    x_constraint: Constraint
    y_constraint: Constraint
    vertical_velocity: Acceleration
    horizontal_velocity: Acceleration
    width: int
    height: int
    color: Tuple[int, int, int]

    def draw(self, window) -> None:
        pygame.draw.rect(window, self.color, (self.x, self.y, self.width, self.height))

    def accelerate_horizontally(self, amount: Acceleration) -> None:
        self.horizontal_velocity += amount

    def accelerate_vertically(self, amount: Acceleration) -> None:
        self.vertical_velocity += amount

    def move_horizontally(self) -> None:
        new_x = self.x + self.horizontal_velocity
        if (new_x > self.x_constraint.min) and (new_x + self.width < self.x_constraint.max):
            self.x = new_x
        else:
            self.horizontal_velocity = 0.

    def move_vertically(self) -> None:
        new_y = self.y + self.vertical_velocity
        if (new_y > self.y_constraint.min) and (new_y + self.height < self.y_constraint.max):
            self.y = new_y
        else:
            self.vertical_velocity = 0.

    def get_shape(self) -> Tuple[int, int]:
        return self.width, self.height

    def is_at_constraints(self):
        new_x = self.x + self.horizontal_velocity
        new_y = self.y + self.vertical_velocity
        vertical_constraint = (new_y > self.y_constraint.min) and (new_y + self.height < self.y_constraint.max)
        horizontal_constraint = (new_x > self.x_constraint.min) and (new_x + self.width < self.x_constraint.max)
        return (not vertical_constraint) or (not horizontal_constraint)


class KeyProtocol(Enum):
    LEFT = auto()
    RIGHT = auto()
    UP = auto()
    DOWN = auto()
    SHOOT = auto()


class KeyResolverInterface:
    def resolve(self, event: KeyId) -> KeyProtocol:
        pass


class DictionaryKeyResolver(KeyResolverInterface):
    def __init__(self, dictionary: Dict[KeyId, KeyProtocol]) -> None:
        self.dictionary = dictionary

    def resolve(self, event: KeyId) -> KeyProtocol:
        return self.dictionary.get(event)


class Player:
    def __init__(self, event_resolver: KeyResolverInterface, entity: Entity, hitpoints: HitPoint, game_controller: GameController, side: int, max_ammo: int, max_acceleration: float) -> None:
        self.event_resolver = event_resolver
        self.entity = entity
        self.hitpoints = hitpoints
        self.game_controller: GameController = game_controller
        self.side = side
        self.max_ammo = max_ammo
        self.ammo_left = self.max_ammo
        self.max_acceleration = max_acceleration
        self.shoot_countdown = 0
        self.ammo_countdown = -1

    def draw(self, window) -> None:
        self.entity.draw(window)

    def accelerate_left(self) -> None:
        if abs(self.entity.horizontal_velocity - 1.) < self.max_acceleration:
            self.entity.horizontal_velocity -= 1.

    def accelerate_right(self) -> None:
        if abs(self.entity.horizontal_velocity + 1.) < self.max_acceleration:
            self.entity.horizontal_velocity += 1.

    def accelerate_up(self) -> None:
        if abs(self.entity.vertical_velocity - 1.) < self.max_acceleration:
            self.entity.vertical_velocity -= 1.

    def accelerate_down(self) -> None:
        if abs(self.entity.vertical_velocity + 1.) < self.max_acceleration:
            self.entity.vertical_velocity += 1.

    def update_position(self) -> None:
        self.entity.move_vertically()
        self.entity.move_horizontally()


    def shoot(self) -> None:
        if self.shoot_countdown <= 0 and self.ammo_left > 0:
            self.game_controller.add_projectile(
                Bullet(
                    Entity(
                        self.entity.x + self.entity.width//2,
                        self.entity.y + (self.entity.height + 10 if self.side == 1 else -10),
                        None,
                        Constraint(0, self.game_controller.config.width),
                        Constraint(0, self.game_controller.config.height),
                        self.game_controller.config.bullet_velocity * (1. if self.side == 1 else -1.),
                        0,
                        self.game_controller.config.bullet_width,
                        self.game_controller.config.bullet_height,
                        self.game_controller.config.player_1_bullet_color if self.side == 1 else self.game_controller.config.player_2_bullet_color
                    ), 1
                )
            )
            self.shoot_countdown = self.game_controller.config.shoot_cooldown
            self.ammo_left -= 1
        print("PEW PEW!")

    def resolve(self, event: KeyId) -> None:
        resolved = self.event_resolver.resolve(event)
        print(resolved)
        if resolved == KeyProtocol.LEFT:
            self.accelerate_left()
        elif resolved == KeyProtocol.RIGHT:
            self.accelerate_right()
        elif resolved == KeyProtocol.UP:
            self.accelerate_up()
        elif resolved == KeyProtocol.DOWN:
            self.accelerate_down()
        elif resolved == KeyProtocol.SHOOT:
            self.shoot()

    def update_state(self):
        if self.shoot_countdown > 0:
            self.shoot_countdown -= 1
        if self.ammo_left < self.max_ammo:
            if self.ammo_countdown == -1:
                self.ammo_countdown = self.game_controller.config.ammo_countdown
            elif self.ammo_countdown == 0:
                self.ammo_countdown = -1
                self.ammo_left += 1
            else:
                self.ammo_countdown -= 1


class Projectile:
    def __init__(self):
        pass

    def get_damage(self) -> HitPoint:
        pass

    def get_shape(self) -> Tuple[int, int]:
        pass

    def get_coordinates(self) -> Tuple[Coordinate, Coordinate]:
        pass

    def destroy(self) -> None:
        pass

    def update_position(self) -> None:
        pass

    def draw(self, window) -> None:
        pass


class Bullet(Projectile):
    def __init__(self, entity: Entity, damage: HitPoint):
        self.entity = entity
        self.damage = damage

    def get_damage(self) -> HitPoint:
        return self.damage

    def get_shape(self) -> Tuple[int, int]:
        return self.entity.width, self.entity.height

    def get_coordinates(self) -> Tuple[Coordinate, Coordinate]:
        return self.entity.x, self.entity.y

    def destroy(self) -> None:
        self.entity.vertical_acceleration = 0.
        self.entity.horizontal_acceleration = 0.

    def update_position(self) -> None:
        self.entity.move_horizontally()
        self.entity.move_vertically()

    def draw(self, window) -> None:
        self.entity.draw(window)


class GameController:
    def __init__(self, config: Config):
        self.players: List[Player] = []
        self.projectiles: Set[Projectile] = set()
        self.config = config
    
    def add_player(self, player: Player) -> None:
        self.players.append(player)

    def add_projectile(self, projectile: Projectile) -> None:
        self.projectiles.add(projectile)

    def check_collision(self, player: Player, projectile: Projectile) -> None:
        projectile_x, projectile_y = projectile.get_coordinates()
        projectile_width, projectile_height = projectile.get_shape()
        horizontal_collision = (player.entity.x < (projectile_x + projectile_width)) and ((player.entity.x + player.entity.width) > projectile_x)
        vertical_collision = (player.entity.y < (projectile_y + projectile_height)) and ((player.entity.y + player.entity.height) > projectile_y)
        if horizontal_collision and vertical_collision:
            player.hitpoints -= projectile.get_damage()
            projectile.destroy()
            return True
        return False

    def check_collisions(self) -> None:
        persistent_projectiles = set([projectile for player in self.players for projectile in self.projectiles if self.check_collision(player, projectile)])
        self.projectiles = self.projectiles.difference(persistent_projectiles)

    def check_players_hitpoints(self) -> Tuple[bool, bool]:
        return self.players[0].hitpoints < 1, self.players[1].hitpoints < 1

    def check_movement(self) -> None:
        for player in self.players:
            player.update_position()
        persistent_projectiles = set()
        for projectile in self.projectiles:
            projectile.update_position()
            if projectile.entity.is_at_constraints():
                print("Projectile at constraints!")
                projectile.destroy()
                persistent_projectiles.add(projectile)
        self.projectiles = self.projectiles.difference(persistent_projectiles)
                
    def redraw_window(self):
        surface = pygame.Surface((self.config.width, self.config.height))
        surface.fill(([0, 0, 0]))
        self.config.window.blit(surface, (0, 0))
        player_1, player_2 = self.players[0], self.players[1]
        p1_hp = self.config.font.render(f"HP: {player_1.hitpoints}", 1, (255,255,255))
        p2_hp = self.config.font.render(f"HP: {player_2.hitpoints}", 1, (255,255,255))
        self.config.window.blit(p1_hp, (10, 10))
        self.config.window.blit(p2_hp, (10, self.config.height -  50))
        p1_ammo = self.config.font.render(f"Ammo: {player_1.ammo_left}", 1, (255,255,255))
        p2_ammo = self.config.font.render(f"Ammo: {player_2.ammo_left}", 1, (255,255,255))
        self.config.window.blit(p1_ammo, (100, 10))
        self.config.window.blit(p2_ammo, (100, self.config.height -  50))
        p1_cooldown = self.config.font.render(f"CD: {'X' if player_1.shoot_countdown != 0 else 'OK'}", 1, (255,255,255))
        p2_cooldown = self.config.font.render(f"CD: {'X' if player_2.shoot_countdown != 0 else 'OK'}", 1, (255,255,255))
        self.config.window.blit(p1_cooldown, (220, 10))
        self.config.window.blit(p2_cooldown, (220, self.config.height -  50))
        p1_vertical_velocity = self.config.font.render(f"vertical velocity: {player_1.entity.vertical_velocity}", 1, (255,255,255))
        p2_vertical_velocity = self.config.font.render(f"vertical velocity: {player_2.entity.vertical_velocity}", 1, (255,255,255))
        self.config.window.blit(p1_vertical_velocity, (300, 10))
        self.config.window.blit(p2_vertical_velocity, (300, self.config.height -  50))
        p1_horizontal_velocity = self.config.font.render(f"horizontal velocity: {player_1.entity.horizontal_velocity}", 1, (255,255,255))
        p2_horizontal_velocity = self.config.font.render(f"horizontal velocity: {player_2.entity.horizontal_velocity}", 1, (255,255,255))
        self.config.window.blit(p1_horizontal_velocity, (550, 10))
        self.config.window.blit(p2_horizontal_velocity, (550, self.config.height -  50))
        for player in self.players:
            player.draw(self.config.window)
        for projectile in self.projectiles:
            projectile.draw(self.config.window)
        pygame.display.update()

    def check_state(self):
        for player in self.players:
            player.update_state()


def main():
    running = True
    clock = pygame.time.Clock()
    config = Config()
    game_controller = GameController(config)

    player_1_events_dictionary = {
        pygame.K_a: KeyProtocol.LEFT,
        pygame.K_d: KeyProtocol.RIGHT,
        pygame.K_w: KeyProtocol.UP,
        pygame.K_s: KeyProtocol.DOWN,
        pygame.K_SPACE: KeyProtocol.SHOOT
    }
    player_1_entity = Entity(
        config.width / 2, 
        100, 
        None, 
        config.player_1_width_constraint, 
        config.player_1_height_constraint,
        1.,
        0.,
        50,
        50,
        config.player_1_color
    )
    player_1 = Player(
        DictionaryKeyResolver(player_1_events_dictionary), 
        player_1_entity,
        5,
        game_controller,
        1,
        config.ammo_maximum,
        config.max_acceleration
    )

    player_2_events_dictionary = {
        pygame.K_LEFT: KeyProtocol.LEFT,
        pygame.K_RIGHT: KeyProtocol.RIGHT,
        pygame.K_UP: KeyProtocol.UP,
        pygame.K_DOWN: KeyProtocol.DOWN,
        pygame.K_RSHIFT: KeyProtocol.SHOOT
    }
    player_2_entity = Entity(
        config.width / 2, 
        config.height - 100, 
        None, 
        config.player_2_width_constraint, 
        config.player_2_height_constraint,
        -1.,
        0.,
        50,
        50,
        config.player_2_color
    )
    player_2 = Player(
        DictionaryKeyResolver(player_2_events_dictionary), 
        player_2_entity,
        5,
        game_controller,
        2,
        config.ammo_maximum,
        config.max_acceleration
    )

    game_controller.add_player(player_1)
    game_controller.add_player(player_2)

    print(pygame.K_RSHIFT)
    while running:
        clock.tick(config.fps)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        pressed_keys = [i for i, val in enumerate(pygame.key.get_pressed()) if val]
        for key in pressed_keys:
            print(key)
            player_1.resolve(key)
            player_2.resolve(key)

        game_controller.check_movement()
        game_controller.check_collisions()
        game_controller.redraw_window()
        game_controller.check_state()
        p1_dead, p2_dead = game_controller.check_players_hitpoints()
        if p1_dead and p2_dead:
            message = config.font.render(f"DRAW", 1, (255,255,255))
            running = False
        elif p1_dead:
            message = config.font.render(f"P2 WON", 1, (255,255,255))
            running = False
        elif p2_dead:
            message = config.font.render(f"P1 WON", 1, (255,255,255))
            running = False    
    config.window.blit(message, (config.width//2 - 20, config.height//2))
    pygame.display.update()
    pygame.time.wait(5000)


if __name__ == "__main__":
    main()