from __future__ import annotations

from dataclasses import dataclass
from typing import Literal
import pygame


TileState = Literal["active", "hit", "missed"]


@dataclass
class Tile:
    lane_index: int
    type_name: str
    image: pygame.Surface
    x: int
    y: float
    width: int
    height: int
    state: TileState = "active"

    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(self.x, int(self.y), self.width, self.height)


