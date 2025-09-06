from __future__ import annotations

from typing import List, Optional

import pygame

from .constants import BASE_WIDTH, BASE_HEIGHT, HIT_LINE_FRACTION, ROWS_VISIBLE, MISS_TOLERANCE_PX, COLOR_BG, COLOR_LANE_GUIDE, COLOR_HIT_LINE
from .config import GameConfig
from .models import Tile


def calculate_lane_rects(window_width: int, window_height: int, lanes: int) -> List[pygame.Rect]:
    lane_width = window_width // lanes
    rects: List[pygame.Rect] = []
    for i in range(lanes):
        rects.append(pygame.Rect(i * lane_width, 0, lane_width, window_height))
    return rects


def get_hit_line_y(window_height: int, fraction: float = HIT_LINE_FRACTION) -> int:
    return int(window_height * fraction)


def get_tile_size(window_width: int, window_height: int, rows_visible: int = ROWS_VISIBLE) -> tuple[int, int]:
    lane_width = window_width // 4
    tile_height = window_height // rows_visible
    return lane_width, tile_height


def draw_tiles(screen: pygame.Surface, tiles: List[Tile]) -> None:
    for t in tiles:
        if t.state == "active":
            screen.blit(pygame.transform.smoothscale(t.image, (t.width, t.height)), (t.x, int(t.y)))


class Game:
    def __init__(self, screen: pygame.Surface, cfg: GameConfig):
        self.screen = screen
        self.cfg = cfg
        self.window_width, self.window_height = screen.get_size()
        self.lane_rects = calculate_lane_rects(self.window_width, self.window_height, cfg.lanes)
        self.hit_line_y = get_hit_line_y(self.window_height)
        self.tile_width, self.tile_height = get_tile_size(self.window_width, self.window_height)
        self.score = 0
        self.elapsed_time = 0.0
        self.current_speed = cfg.speed.start_px_per_sec
        self.tiles: List[Tile] = []
        self.running = True
        self.game_over = False
        self.last_fail_reason: Optional[str] = None
        self.last_missed_type: Optional[str] = None

    def update_speed(self, dt: float) -> None:
        inc = (self.cfg.speed.accel_px_per_min / 60.0) * dt
        self.current_speed = min(self.current_speed + inc, self.cfg.speed.max_px_per_sec)

    def update(self, dt: float) -> None:
        if self.game_over:
            return
        self.elapsed_time += dt
        self.update_speed(dt)
        for t in self.tiles:
            if t.state == "active":
                t.y += self.current_speed * dt
        self.check_misses()

    def handle_keydown(self, lane_index: int) -> None:
        print(f"DEBUG: handle_keydown lane={lane_index}")
        tile = self.find_tile_at_hit_line(lane_index)
        if tile is None:
            # No tile at the hit line in this lane: ignore tap (not a failure per spec)
            print("DEBUG: no tile intersecting hit line; ignoring tap")
            return
        print(
            f"DEBUG: hit candidate type={tile.type_name} y={tile.y:.1f} h={tile.height} hit_line={self.hit_line_y}"
        )
        if tile.type_name == self.cfg.target_type:
            tile.state = "hit"
            self.score += 1
            print(f"DEBUG: HIT! score={self.score}")
        else:
            self.last_fail_reason = "wrong_tap"
            self.last_missed_type = tile.type_name
            self.game_over = True
            print("DEBUG: WRONG TAP → game over")

    def find_tile_at_hit_line(self, lane_index: int) -> Optional[Tile]:
        # Valid if the hit line intersects the tile's vertical span [y, y+height]
        candidates: list[Tile] = []
        for t in self.tiles:
            if t.state != "active" or t.lane_index != lane_index:
                continue
            if t.y <= self.hit_line_y <= (t.y + t.height):
                candidates.append(t)
        if not candidates:
            return None
        # Choose the one whose center is closest to the hit line
        candidates.sort(key=lambda t: abs((t.y + t.height / 2) - self.hit_line_y))
        return candidates[0]

    def check_misses(self) -> None:
        for t in self.tiles:
            if t.state == "active" and t.type_name == self.cfg.target_type:
                # Miss only after the tile's TOP passes below the hit line (tile entirely below the line)
                if t.y > self.hit_line_y + MISS_TOLERANCE_PX:
                    self.last_fail_reason = "missed_target"
                    self.last_missed_type = self.cfg.target_type
                    self.game_over = True
                    print(
                        f"DEBUG: MISS target type at y={t.y:.1f} passed line={self.hit_line_y} tol={MISS_TOLERANCE_PX}"
                    )
                    return

    def render(self) -> None:
        self.screen.fill(COLOR_BG)
        # lane guides
        for i, rect in enumerate(self.lane_rects):
            if i > 0:
                pygame.draw.line(self.screen, COLOR_LANE_GUIDE, (rect.x, 0), (rect.x, self.window_height), 1)
        # tiles
        draw_tiles(self.screen, self.tiles)
        # hit line on top
        pygame.draw.line(self.screen, COLOR_HIT_LINE, (0, self.hit_line_y), (self.window_width, self.hit_line_y), 2)


