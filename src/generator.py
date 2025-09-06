from __future__ import annotations

import random
from typing import List

import pygame

from .assets import AssetManager
from .models import Tile


def choose_target_lane(rng: random.Random, lanes: int) -> int:
    return rng.randrange(lanes)


def generate_row(
    target_type: str,
    other_types: List[str],
    lanes: int,
    lane_rects: List[pygame.Rect],
    asset_manager: AssetManager,
    tile_height: int,
    rng: random.Random,
    y_top: int,
) -> List[Tile]:
    tiles: List[Tile] = []
    target_lane = choose_target_lane(rng, lanes)
    for lane_idx in range(lanes):
        lane_rect = lane_rects[lane_idx]
        x = lane_rect.x
        width = lane_rect.width
        if lane_idx == target_lane:
            img = asset_manager.get_random_image(target_type)
            tiles.append(Tile(lane_index=lane_idx, type_name=target_type, image=img, x=x, y=y_top, width=width, height=tile_height))
        else:
            if other_types:
                t = rng.choice(other_types)
                img = asset_manager.get_random_image(t)
                tiles.append(Tile(lane_index=lane_idx, type_name=t, image=img, x=x, y=y_top, width=width, height=tile_height))
            else:
                # No other types: leave lane empty for this row
                pass
    return tiles


