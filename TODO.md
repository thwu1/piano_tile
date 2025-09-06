## TODO — Piano Tiles (Image Types) Implementation Plan

This checklist enumerates every step to implement the game exactly per `README.md` and `design.md`. Each item includes concrete function names, arguments, and expected behavior.

### 0) Environment

- [ ] Install Python 3.10+ and dependencies
  - Command: `pip install pygame pillow`

### 1) Project scaffolding

- [ ] Create directories and files
  - `assets/` (contains only type directories)
  - `src/`
    - `main.py`
    - `config.py`
    - `assets.py`
    - `models.py`
    - `generator.py`
    - `game.py`
    - `hud.py`
    - `constants.py`
  - `config.json`

### 2) Config loader and validation (`src/config.py`)

- [ ] Define dataclasses
  - `SpeedConfig(start_px_per_sec: float, accel_px_per_min: float, max_px_per_sec: float)`
  - `HitWindowConfig(good: int)`
  - `ControlsConfig(keys: list[str])`
  - `GameConfig(lanes: int, mode: str, target_type: str, other_types: list[str], speed: SpeedConfig, hit_window_ms: HitWindowConfig, assets_root: str, supported_formats: list[str], controls: ControlsConfig)`

- [ ] Implement `load_config(path: str) -> GameConfig`
  - Read JSON from `path`, parse into dataclasses.

- [ ] Implement `validate_config(cfg: GameConfig) -> None`
  - Ensure `cfg.mode == "endless"`.
  - Ensure `cfg.lanes == 4` (as per current rules) or >=1 if allowing future-proofing.
  - Ensure `cfg.target_type` not empty.
  - Ensure all entries in `cfg.supported_formats` are exactly in {"png","jpg"}.
  - Ensure `cfg.controls.keys` length equals `cfg.lanes` and keys are unique.
  - Ensure `cfg.speed.max_px_per_sec >= cfg.speed.start_px_per_sec` and all > 0.

### 3) Synthetic asset generation (`src/assets.py`)

- [ ] Implement `ensure_synthetic_assets(assets_root: str) -> None`
  - Create `assets_root/synth_a` and `assets_root/synth_b` if missing.
  - Ensure each has exactly 4 images named `img_1.png` … `img_4.png`.
  - Use Pillow only.

- [ ] Implement helper `create_labeled_image(path: str, size: tuple[int,int], background_rgb: tuple[int,int,int], text: str) -> None`
  - Create 256×256 PNG with solid background and centered text label.
  - Use Pillow `Image`, `ImageDraw`, `ImageFont` (default font if none available).

### 4) AssetManager — discovery and preload (`src/assets.py`)

- [ ] Implement `discover_types(assets_root: str) -> list[str]`
  - List immediate entries in `assets_root`; keep only directories; return their names as `type_name`s.

- [ ] Implement `validate_assets_root(assets_root: str) -> None`
  - Ensure every entry in `assets_root` is a directory. Error if files or unexpected entries exist.

- [ ] Implement `list_images_for_type(type_dir: str, supported_formats: list[str]) -> list[str]`
  - Return file paths with extensions matching supported formats (case-insensitive).

- [ ] Implement `load_and_scale_image(path: str, tile_size: tuple[int,int]) -> pygame.Surface`
  - Load image, center-crop or letterbox to fit `tile_size`, return `Surface`.

- [ ] Implement class `AssetManager`
  - `__init__(self, assets_root: str, supported_formats: list[str], tile_size: tuple[int,int])`
  - `type_to_surfaces: dict[str, list[pygame.Surface]]`
  - `preload(self) -> None`
    - Calls `validate_assets_root`, `discover_types`, then loads/scales images per type.
  - `get_random_image(self, type_name: str) -> pygame.Surface`
    - Random uniform selection among preloaded surfaces for `type_name`.
  - `get_thumbnail(self, type_name: str, thumb_size: tuple[int,int]) -> pygame.Surface`
    - Return a scaled copy of a representative image for HUD.

### 5) Geometry and layout helpers (`src/constants.py` and `src/game.py`)

- [ ] Define constants in `constants.py`
  - `BASE_WIDTH = 480`, `BASE_HEIGHT = 800`
  - `HIT_LINE_FRACTION = 0.88`
  - `ROWS_VISIBLE = 4` (guidance for tile height)
  - Colors: `COLOR_BG`, `COLOR_HIT_LINE`, `COLOR_HUD_TEXT`, etc.

- [ ] Implement geometry helpers in `game.py`
  - `calculate_lane_rects(window_width: int, window_height: int, lanes: int) -> list[pygame.Rect]`
  - `get_hit_line_y(window_height: int, fraction: float = HIT_LINE_FRACTION) -> int`
  - `get_tile_size(window_width: int, window_height: int, rows_visible: int = ROWS_VISIBLE) -> tuple[int,int]`

### 6) Models (`src/models.py`)

- [ ] Define `enum.Enum` or `Literal` for tile state
  - `TileState = Literal["active", "hit", "missed"]`

- [ ] Define `Tile` dataclass
  - Fields: `lane_index: int`, `type_name: str`, `image: pygame.Surface`, `x: int`, `y: float`, `width: int`, `height: int`, `state: TileState`
  - Method: `get_rect(self) -> pygame.Rect`

### 7) Row/tile generation (`src/generator.py`)

- [ ] Implement `choose_target_lane(rng: random.Random, lanes: int) -> int`

- [ ] Implement `generate_row(target_type: str, other_types: list[str], lanes: int, lane_rects: list[pygame.Rect], asset_manager: AssetManager, tile_height: int, rng: random.Random) -> list[Tile]`
  - Select one lane as target, fill others with random types from `other_types` (uniform). If `other_types` is empty, leave other lanes empty tiles list (only target).

- [ ] Implement `initial_rows(num_rows: int, start_y: int, row_spacing: int, ...) -> list[Tile]`
  - Seed initial off-screen rows above the window if desired.

### 8) Speed and timing helpers (`src/game.py`)

- [ ] Implement `update_speed(current_speed: float, accel_px_per_min: float, dt_sec: float, max_px_per_sec: float) -> float`
  - Increase linearly by `accel_px_per_min / 60 * dt_sec`, clamp to `max_px_per_sec`.

- [ ] Implement `pixels_for_hit_window(speed_px_per_sec: float, hit_window_ms: int) -> float`
  - Convert timing window to pixel distance at current speed.

### 9) Input mapping (`src/game.py`)

- [ ] Implement `key_to_lane(key: int, keys: list[str]) -> int | None`
  - Map pygame key to lane index by matching against configured `keys` (H, J, K, L).

### 10) Game logic (`src/game.py`)

- [ ] Implement class `Game`
  - `__init__(self, screen: pygame.Surface, cfg: GameConfig, asset_manager: AssetManager)`
    - Compute geometry; cache `lane_rects`, `hit_line_y`, `tile_size`.
    - Initialize state: `score=0`, `elapsed_time=0.0`, `current_speed=cfg.speed.start_px_per_sec`, `tiles=[]`, `running=True`, `game_over=False`.
    - Pre-generate first rows.
  - `reset(self) -> None`
    - Reset score, time, speed, tiles, and flags.
  - `spawn_row_if_needed(self) -> None`
    - Based on last row position and a spacing threshold (e.g., tile height).
  - `update(self, dt: float) -> None`
    - Increment `elapsed_time`.
    - Update `current_speed` via `update_speed`.
    - Move tiles: `tile.y += current_speed * dt`.
    - Call `check_misses()`; if miss on a target tile, set `game_over=True`.
    - Call `spawn_row_if_needed()`.
  - `handle_keydown(self, lane_index: int) -> None`
    - Find nearest tile in lane around hit line using `find_hittable_tile`.
    - If found and `tile.type_name == cfg.target_type`: mark `hit`, `score += 1` and remove/hide tile.
    - Else: `game_over = True`.
  - `find_hittable_tile(self, lane_index: int, hit_window_px: float) -> Tile | None`
    - Choose the tile in `active` state closest to `hit_line_y` within `hit_window_px`.
  - `check_misses(self) -> None`
    - If any `active` target tile `y` passes below `hit_line_y + tolerance` without being hit → `game_over = True`.
  - `render(self) -> None`
    - Draw background, lanes, tiles, hit line, and call `render_hud`.

### 11) Rendering helpers (`src/game.py` and `src/hud.py`)

- [ ] Implement `draw_tiles(screen: pygame.Surface, tiles: list[Tile]) -> None`
  - Blit `tile.image` at `(tile.x, int(tile.y))` for `state == "active"`.

- [ ] Implement `render_hud(screen: pygame.Surface, font: pygame.font.Font, target_thumb: pygame.Surface, score: int, elapsed_time: float, timer_full_scale_sec: float, window_width: int) -> None`
  - Draw small target thumbnail/icon, score text, and a timer/progress bar based on `elapsed_time` and `timer_full_scale_sec` (e.g., 60s to fill the bar).

### 12) Main loop and bootstrap (`src/main.py`)

- [ ] Implement `init_pygame_window(width: int, height: int, caption: str) -> pygame.Surface`

- [ ] Implement `run() -> None`
  - Load config: `cfg = load_config("config.json"); validate_config(cfg)`.
  - Ensure synthetic assets: `ensure_synthetic_assets(cfg.assets_root)`.
  - Compute `tile_size` using base window size and `ROWS_VISIBLE`.
  - Create `AssetManager(cfg.assets_root, cfg.supported_formats, tile_size)` and `preload()`.
  - Create window and `Game` instance.
  - Main loop:
    - `dt = clock.tick(60)/1000`
    - Handle events: QUIT; KEYDOWN → map to lane via `key_to_lane` and call `game.handle_keydown`.
    - If not `game_over`: `game.update(dt)`.
    - `game.render()`; `pygame.display.flip()`.
  - On game over: show overlay with score; wait for key to restart or quit.

### 13) Game over overlay (`src/game.py` or `src/main.py`)

- [ ] Implement `render_game_over(screen: pygame.Surface, font: pygame.font.Font, score: int, window_size: tuple[int,int]) -> None`
  - Semi-transparent overlay, centered text: "Game Over" and `Score: N`.

- [ ] Implement `wait_for_restart_or_quit() -> str`
  - Block until user presses `R` to restart or `ESC/Q` to quit; return action.

### 14) Error handling and validation

- [ ] In `main.run`, validate that `cfg.target_type` exists under `assets_root`.
- [ ] Validate that each `type_name` directory contains at least 1 image.
- [ ] If `other_types` contains names not present in assets, log error and ignore or exit (decide policy; recommended: exit with message).

### 15) Performance considerations

- [ ] Pre-scale all images on load; avoid per-frame transforms.
- [ ] Use a single `pygame.font.Font` instance cached in HUD.
- [ ] Avoid per-frame file system access.

### 16) Defaults and constants tuning

- [ ] Set default `timer_full_scale_sec = 60.0` (used purely for HUD progress bar visualization).
- [ ] Set `ROW_SPACING_PX = tile_height` (one tile per row spacing) and adjust as needed.

### 17) Minimal tests/manual checks

- [ ] Launch with only synthetic assets (`synth_a` target, `synth_b` others); verify rows contain exactly one target tile.
- [ ] Verify H/J/K/L hit detection works and increments score only on target hits.
- [ ] Verify missing a target or hitting a non-target ends the game.
- [ ] Verify speed ramps and caps at `max_px_per_sec`.
- [ ] Verify HUD shows target thumbnail, score, and timer bar.


