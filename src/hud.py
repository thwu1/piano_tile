from __future__ import annotations

import pygame
from .constants import COLOR_HUD_TEXT, COLOR_TIMER


def render_hud(
    screen: pygame.Surface,
    font: pygame.font.Font,
    target_thumb: pygame.Surface,
    score: int,
    elapsed_time: float,
    timer_full_scale_sec: float,
    window_width: int,
) -> None:
    # Target thumbnail
    screen.blit(target_thumb, (8, 8))
    # Score text
    score_surf = font.render(f"Score: {score}", True, COLOR_HUD_TEXT)
    screen.blit(score_surf, (8 + target_thumb.get_width() + 10, 12))
    # Timer bar (purely visual)
    fill_frac = min(1.0, elapsed_time / max(0.001, timer_full_scale_sec))
    bar_w = int(window_width * 0.4)
    bar_h = 8
    x = window_width - bar_w - 12
    y = 16
    pygame.draw.rect(screen, (60, 60, 60), pygame.Rect(x, y, bar_w, bar_h), 1)
    pygame.draw.rect(screen, COLOR_TIMER, pygame.Rect(x + 1, y + 1, int((bar_w - 2) * fill_frac), bar_h - 2))



def render_hud_classic(
    screen: pygame.Surface,
    font: pygame.font.Font,
    target_thumb: pygame.Surface,
    cleared_rows: int,
    rows_total: int,
    elapsed_time: float,
    window_width: int,
) -> None:
    # Target thumbnail
    screen.blit(target_thumb, (8, 8))
    # Rows progress
    rows_text = f"Rows: {cleared_rows}/{rows_total}"
    rows_surf = font.render(rows_text, True, COLOR_HUD_TEXT)
    screen.blit(rows_surf, (8 + target_thumb.get_width() + 10, 12))
    # Timer (mm:ss.ms)
    total_ms = int(elapsed_time * 1000)
    minutes = total_ms // 60000
    seconds = (total_ms % 60000) // 1000
    centis = (total_ms % 1000) // 10
    time_text = f"{minutes:02d}:{seconds:02d}.{centis:02d}"
    time_surf = font.render(time_text, True, COLOR_TIMER)
    screen.blit(time_surf, (window_width - time_surf.get_width() - 12, 12))

