from __future__ import annotations

import json
from dataclasses import dataclass
from typing import List


@dataclass
class SpeedConfig:
    start_px_per_sec: float
    accel_px_per_min: float
    max_px_per_sec: float


@dataclass
class HitWindowConfig:
    good: int


@dataclass
class ControlsConfig:
    keys: List[str]

@dataclass
class ClassicConfig:
    rows_total: int
    advance_animation_ms: int = 160


@dataclass
class GameConfig:
    lanes: int
    mode: str
    target_type: str
    other_types: List[str]
    speed: SpeedConfig
    hit_window_ms: HitWindowConfig
    assets_root: str
    supported_formats: List[str]
    controls: ControlsConfig
    classic: ClassicConfig | None


def load_config(path: str) -> GameConfig:
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)
    speed = SpeedConfig(**raw["speed"])
    # Ignore unknown fields in hit_window_ms (e.g., 'perfect' if present)
    hit_win_raw = raw["hit_window_ms"]
    hit = HitWindowConfig(good=int(hit_win_raw["good"]))
    controls = ControlsConfig(keys=list(raw["controls"]["keys"]))
    mode = str(raw["mode"]).lower()
    classic: ClassicConfig | None = None
    if mode == "classic":
        classic_raw = raw.get("classic", {})
        classic = ClassicConfig(
            rows_total=int(classic_raw["rows_total"]),
            advance_animation_ms=int(classic_raw.get("advance_animation_ms", 160)),
        )
    cfg = GameConfig(
        lanes=int(raw["lanes"]),
        mode=str(raw["mode"]),
        target_type=str(raw["target_type"]),
        other_types=list(raw["other_types"]),
        speed=speed,
        hit_window_ms=hit,
        assets_root=str(raw["assets_root"]),
        supported_formats=[s.lower() for s in raw["supported_formats"]],
        controls=controls,
        classic=classic,
    )
    return cfg


def validate_config(cfg: GameConfig) -> None:
    if cfg.mode not in {"endless", "classic"}:
        raise ValueError("mode must be one of {'endless','classic'}")
    if cfg.lanes != 4:
        raise ValueError("lanes must be exactly 4 per current spec")
    if not cfg.target_type:
        raise ValueError("target_type must be provided")
    allowed_exts = {"png", "jpg"}
    if not set(cfg.supported_formats).issubset(allowed_exts):
        raise ValueError("supported_formats must be subset of {'png','jpg'}")
    if len(cfg.controls.keys) != cfg.lanes:
        raise ValueError("controls.keys length must equal lanes")
    if len(set(k.lower() for k in cfg.controls.keys)) != len(cfg.controls.keys):
        raise ValueError("controls.keys must be unique (case-insensitive)")
    if cfg.mode == "endless":
        if cfg.speed.start_px_per_sec <= 0 or cfg.speed.accel_px_per_min < 0 or cfg.speed.max_px_per_sec <= 0:
            raise ValueError("speed values must be positive and accel non-negative")
        if cfg.speed.max_px_per_sec < cfg.speed.start_px_per_sec:
            raise ValueError("max_px_per_sec must be >= start_px_per_sec")
    if cfg.mode == "classic":
        if cfg.classic is None:
            raise ValueError("classic config section is required for classic mode")
        if cfg.classic.rows_total <= 0:
            raise ValueError("classic.rows_total must be > 0")
        if cfg.classic.advance_animation_ms < 0:
            raise ValueError("classic.advance_animation_ms must be >= 0")

