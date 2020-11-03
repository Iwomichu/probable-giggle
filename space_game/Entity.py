from dataclasses import dataclass
from typing import Tuple

import pygame

from space_game.domain_names import Constraint, Coordinate, Acceleration


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
    max_velocity: Acceleration
    acceleration: Acceleration = 0.

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

    def accelerate_left(self) -> None:
        if abs(self.horizontal_velocity - self.acceleration) < self.max_velocity:
            self.horizontal_velocity -= self.acceleration

    def accelerate_right(self) -> None:
        if abs(self.horizontal_velocity + self.acceleration) < self.max_velocity:
            self.horizontal_velocity += self.acceleration

    def accelerate_up(self) -> None:
        if abs(self.vertical_velocity - self.acceleration) < self.max_velocity:
            self.vertical_velocity -= self.acceleration

    def accelerate_down(self) -> None:
        if abs(self.vertical_velocity + self.acceleration) < self.max_velocity:
            self.vertical_velocity += self.acceleration

    def get_coordinates(self):
        return self.x, self.y

    def update_position(self):
        self.move_vertically()
        self.move_horizontally()
