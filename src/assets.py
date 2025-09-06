from __future__ import annotations

import os
import random
from typing import Dict, List, Tuple

import pygame
from PIL import Image





def discover_types(assets_root: str) -> List[str]:
    entries = []
    for name in os.listdir(assets_root):
        full = os.path.join(assets_root, name)
        if os.path.isdir(full):
            entries.append(name)
    return sorted(entries)


def validate_expected_type_dirs(assets_root: str, expected_types: set[str]) -> None:
    actual_dirs = {name for name in os.listdir(assets_root) if os.path.isdir(os.path.join(assets_root, name))}
    missing = expected_types - actual_dirs
    extra = actual_dirs - expected_types
    if missing:
        raise FileNotFoundError(f"Missing type directories: {sorted(missing)}")
    if extra:
        raise ValueError(f"Unexpected extra type directories in assets_root: {sorted(extra)}")


def list_images_for_type(type_dir: str, supported_formats: List[str]) -> List[str]:
    allowed = {ext.lower() for ext in supported_formats}
    files = []
    for fname in os.listdir(type_dir):
        full = os.path.join(type_dir, fname)
        if os.path.isfile(full):
            ext = os.path.splitext(fname)[1].lower().lstrip(".")
            if ext in allowed:
                files.append(full)
    return sorted(files)


def load_and_scale_image(path: str, tile_size: Tuple[int, int]) -> pygame.Surface:
    img = Image.open(path).convert("RGB")
    target_w, target_h = tile_size
    # Stretch to fill exactly tile rect (no bars, no crops)
    stretched = img.resize((target_w, target_h), Image.LANCZOS)
    mode = stretched.mode
    data = stretched.tobytes()
    surface = pygame.image.fromstring(data, stretched.size, mode)
    return surface


class AssetManager:
    def __init__(self, assets_root: str, supported_formats: List[str], tile_size: Tuple[int, int]):
        self.assets_root = assets_root
        self.supported_formats = [ext.lower() for ext in supported_formats]
        self.tile_size = tile_size
        self.type_to_surfaces: Dict[str, List[pygame.Surface]] = {}

    def preload(self, types: List[str]) -> None:
        for type_name in types:
            tdir = os.path.join(self.assets_root, type_name)
            paths = list_images_for_type(tdir, self.supported_formats)
            if not paths:
                raise FileNotFoundError(f"No images found for type '{type_name}' in {tdir}")
            surfaces = [load_and_scale_image(p, self.tile_size) for p in paths]
            self.type_to_surfaces[type_name] = surfaces

    def get_random_image(self, type_name: str) -> pygame.Surface:
        surfaces = self.type_to_surfaces.get(type_name)
        if not surfaces:
            raise KeyError(f"Type '{type_name}' not loaded")
        return random.choice(surfaces)

    def get_thumbnail(self, type_name: str, thumb_size: Tuple[int, int]) -> pygame.Surface:
        base = self.get_random_image(type_name)
        # Create a copy and scale
        thumb = pygame.transform.smoothscale(base, thumb_size)
        return thumb


