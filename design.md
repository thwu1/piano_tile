## Piano Tiles (Image Types) — Implementation Design (Python, pygame)

### Overview

Endless-mode Piano Tiles variant where tiles are images from named types under `assets/{type_name}` (PNG/JPG only). One fixed `target_type` is configured; each row spawns exactly one target tile and fills remaining lanes with other types. Player taps only target tiles; tapping any other type or missing a target ends the run. Scoring is base-only (+1 per correct tap). Four lanes are mapped to `H J K L`.

### Tech stack

- Python 3.10+
- `pygame` for rendering, input, timing

### Directory structure

- `assets/<type_name>/*` image files (PNG/JPG)
- `config.json` (runtime settings)
- `src/`
  - `main.py` (entry point; bootstraps everything)
  - `config.py` (load/validate config)
  - `assets.py` (AssetManager)
  - `models.py` (Tile, enums/constants)
  - `generator.py` (row/tile generation)
  - `game.py` (Game state and loop)
  - `hud.py` (HUD rendering)
  - `constants.py` (colors, defaults)

### Configuration

- `lanes: 4`
- `mode: "endless"`
- `target_type: "synth_a"` (default)
- `other_types: ["synth_b"]` (default)
- `speed: { start_px_per_sec, accel_px_per_min, max_px_per_sec }`
- `hit_window_ms: { good }` — only the “good” window is used; any `perfect` value is ignored if present
- `assets_root: "assets"`
- `supported_formats: ["png", "jpg"]`
- `controls: { keys: ["H","J","K","L"] }`

Example:

```json
{
  "lanes": 4,
  "mode": "endless",
  "target_type": "synth_a",
  "other_types": ["synth_b"],
  "speed": { "start_px_per_sec": 400, "accel_px_per_min": 250, "max_px_per_sec": 1200 },
  "hit_window_ms": { "good": 120 },
  "assets_root": "assets",
  "supported_formats": ["png", "jpg"],
  "controls": { "keys": ["H", "J", "K", "L"] }
}
```

### Game flow and systems

- AssetManager (`assets.py`)
  - Discover types by listing immediate subdirectories of the assets root (non-recursive). Each subdirectory name is a `type_name`.
  - Validate the assets root contains only type directories (no files or unrelated folders at this level). Error if unexpected entries are found.
  - Load PNG/JPG from each type directory as `pygame.Surface`.
  - Pre-scale to tile size; center-crop or letterbox/pillarbox to preserve aspect ratios.
  - API: `get_random_image(type_name) -> Surface`.

- Tile model (`models.py`)
  - `Tile` fields: `lane_index`, `type_name`, `image`, `y`, `width`, `height`, `state` in {`active`, `hit`, `missed`}.

- Row generation (`generator.py`)
  - For each new row: choose a random lane for the `target_type`. For remaining lanes, pick uniformly from `other_types`.
  - Instantiate `Tile` objects with images via AssetManager.

- Game state & loop (`game.py`)
  - State: score, elapsed_time, `current_speed`, tile list, lane geometry, hit line Y.
  - Update per frame:
    - `dt = clock.tick(fps)/1000`
    - Increase speed linearly: `current_speed = min(current_speed + accel*dt, max_speed)`
    - Move tiles: `tile.y += current_speed * dt`
    - Miss detection: if a target tile crosses the hit line without being hit → game over.
    - Spawn new rows when top spacing threshold is met.

- Input handling (H/J/K/L)
  - Map key to lane index (0..3).
  - On keydown, find the nearest tile in that lane within the vertical hit window around the hit line.
  - If tile exists and `type_name == target_type`: mark `hit`, score += 1; otherwise: game over.

- HUD (`hud.py`)
  - Draw current `target_type` thumbnail, `score`, and a `timer` bar (based on elapsed run time).

- Difficulty ramp
  - Linear acceleration over time, capped at `max_px_per_sec`.

- Game over
  - Full-screen overlay showing final score and a brief message; allow restart or quit.

### Geometry and rendering

- Suggested base resolution: 480×800 (portrait). Compute `lane_width = window_width / lanes`.
- Tile height proportional to window height (e.g., enough for ~4 rows visible).
- Hit line near bottom (≈ 88% of height). Draw as a thin guide line.
- Draw order: background → tiles → hit effects → HUD.

### Hit window

- Use `hit_window_ms.good`. Convert to pixels with current speed for proximity checks, or compare times by extrapolating crossing time to the hit line.

### Synthetic asset generation

- Requirement: create two synthetic types with four images each:
  - `assets/synth_a/img_1.png` … `img_4.png`
  - `assets/synth_b/img_1.png` … `img_4.png`

- Image spec
  - 256×256 PNG, solid background color per type, centered label text (e.g., `SYNTH_A_1`).

- Implementation sketch (generator)
  - Use `Pillow` to create images.

```python
def ensure_synthetic_assets(assets_root: str) -> None:
  # create assets/synth_a and assets/synth_b with 4 labeled PNGs each, if missing
  pass
```

### Performance considerations

- Preload and pre-scale all images at startup; avoid per-frame scaling and disk I/O.
- Use integer-aligned blits when possible; minimize surface conversions in the loop.

### Edge cases

- `other_types` may be empty; rows still spawn exactly one `target_type` tile.
- Missing or empty asset folders: fail clearly; if synthetic defaults are selected, auto-generate them.
- Mixed image sizes/aspect ratios: maintain aspect with center-crop or letterbox.

### Milestones

1. Project scaffolding, config loader, constants.
2. AssetManager with preload/scale and synthetic asset generator.
3. Lane geometry and background rendering test.
4. Tile model, simple row spawn, vertical scrolling.
5. Hit line, hit detection, base scoring.
6. Speed ramp with max cap.
7. HUD: target icon, score, timer bar.
8. Game over overlay and restart flow.

### How to run

```bash
pip install pygame
python -m src.main
```


