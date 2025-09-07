from __future__ import annotations

import os
import sys
import time
import random
import pygame

from .config import load_config, validate_config
from .constants import BASE_WIDTH, BASE_HEIGHT, ROWS_VISIBLE
from .assets import AssetManager, validate_expected_type_dirs
from .game import Game, calculate_lane_rects, get_hit_line_y, get_tile_size
from .generator import generate_row
from .hud import render_hud


def normalize_keys_to_pygame(keys):
    # Accept any pygame key name (e.g., "a", "space", "left").
    # Returns a list of pygame key codes; raises ValueError on invalid names or duplicates.
    result: list[int] = []
    for raw in keys:
        if isinstance(raw, str):
            name = raw.strip().lower()
            try:
                code = pygame.key.key_code(name)
            except Exception as exc:
                raise ValueError(f"Invalid key name in controls.keys: {raw}") from exc
            result.append(code)
        else:
            raise ValueError("controls.keys items must be strings representing pygame key names")

    if len(set(result)) != len(result):
        raise ValueError("controls.keys must map to unique keys")
    return result


def key_to_lane(key: int, keys: list[int]) -> int | None:
    for idx, k in enumerate(keys):
        if key == k:
            return idx
    return None


def init_pygame_window(width: int, height: int, caption: str) -> pygame.Surface:
    pygame.init()
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption(caption)
    return screen


def run() -> None:
    cfg = load_config(os.path.join(os.path.dirname(__file__), "..", "config.json"))
    validate_config(cfg)

    # Validate assets exist for configured types
    validate_expected_type_dirs(cfg.assets_root, {cfg.target_type, *cfg.other_types})

    screen = init_pygame_window(BASE_WIDTH, BASE_HEIGHT, "Piano Tiles (Images)")
    clock = pygame.time.Clock()

    lane_rects = calculate_lane_rects(BASE_WIDTH, BASE_HEIGHT, cfg.lanes)
    tile_w, tile_h = get_tile_size(BASE_WIDTH, BASE_HEIGHT, ROWS_VISIBLE)

    asset_manager = AssetManager(cfg.assets_root, cfg.supported_formats, (tile_w, tile_h))
    # Preload only configured types
    asset_manager.preload([cfg.target_type, *cfg.other_types])

    game = Game(screen, cfg)
    # Seed initial rows
    rng = random.Random()
    start_y = -tile_h
    spacing = tile_h
    for i in range(ROWS_VISIBLE + 1):
        row_y = start_y - i * spacing
        game.tiles.extend(
            generate_row(cfg.target_type, cfg.other_types, cfg.lanes, lane_rects, asset_manager, tile_h, rng, row_y)
        )

    font = pygame.font.SysFont(None, 24)
    target_thumb = asset_manager.get_thumbnail(cfg.target_type, (40, 40))
    timer_full_scale_sec = 60.0

    keys_norm = normalize_keys_to_pygame(cfg.controls.keys)

    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                print(f"DEBUG: keydown key={event.key}")
                lane_idx = key_to_lane(event.key, keys_norm)
                if lane_idx is not None and not game.game_over:
                    game.handle_keydown(lane_idx)
                elif event.key == pygame.K_r and game.game_over:
                    # Simple restart: re-run main
                    run()
                    return
                elif event.key in (pygame.K_ESCAPE, pygame.K_q):
                    running = False

        if not game.game_over:
            game.update(dt)
            # Spawn new rows based on the topmost tile position
            active_tiles = [t for t in game.tiles if t.state == "active"]
            if active_tiles:
                top_y = min(t.y for t in active_tiles)
            else:
                top_y = 1e9
            if top_y >= 0:
                game.tiles.extend(
                    generate_row(
                        cfg.target_type,
                        cfg.other_types,
                        cfg.lanes,
                        lane_rects,
                        asset_manager,
                        tile_h,
                        rng,
                        -tile_h,
                    )
                )

        game.render()

        # HUD
        render_hud(screen, font, target_thumb, game.score, game.elapsed_time, timer_full_scale_sec, BASE_WIDTH)

        # Simple game over overlay
        if game.game_over:
            overlay = pygame.Surface((BASE_WIDTH, BASE_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            screen.blit(overlay, (0, 0))
            go_font = pygame.font.SysFont(None, 48)
            txt1 = go_font.render("Game Over", True, (255, 255, 255))
            txt2 = font.render(f"Score: {game.score}", True, (255, 255, 255))
            reason = game.last_fail_reason or ""
            missed = f"Missed: {game.last_missed_type}" if game.last_missed_type else ""
            txt3 = font.render((missed or reason), True, (255, 200, 200))
            screen.blit(txt1, (BASE_WIDTH // 2 - txt1.get_width() // 2, BASE_HEIGHT // 2 - 60))
            screen.blit(txt2, (BASE_WIDTH // 2 - txt2.get_width() // 2, BASE_HEIGHT // 2))
            if txt3.get_width() > 0:
                screen.blit(txt3, (BASE_WIDTH // 2 - txt3.get_width() // 2, BASE_HEIGHT // 2 + 28))
            hint = font.render("Press R to restart, ESC/Q to quit", True, (200, 200, 200))
            screen.blit(hint, (BASE_WIDTH // 2 - hint.get_width() // 2, BASE_HEIGHT // 2 + 60))

        pygame.display.flip()


if __name__ == "__main__":
    run()


