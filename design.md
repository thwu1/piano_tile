## Piano Tiles (Image Types) — Implementation Design (Python, pygame)

### Overview

Piano Tiles variant where tiles are images from named types under `assets/{type_name}` (PNG/JPG only). Supports two modes selected by `mode` in config:
- Endless: one fixed `target_type`; each row spawns exactly one target tile and fills remaining lanes with other types; tiles scroll continuously; tapping any other type or missing a target ends the run; scoring is base-only (+1 per correct tap).
- Classic: fixed-length run measured by time; the board advances one row only after a correct hit; a wrong hit ends the run; objective is to finish all rows as fast as possible.

Four lanes are mapped left→right via configurable `controls.keys`.

### Tech stack

- Python 3.10+
- `pygame` for rendering, input, timing

### Environment (conda)

- Use a dedicated conda environment named `piano_tile`.
- Setup commands:

```bash
conda create -y -n piano_tile python=3.12
conda run -n piano_tile python -m pip install --upgrade pip
conda run -n piano_tile python -m pip install pygame pillow
```

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
- `mode: "endless" | "classic"`
- `target_type: "<type_name>"`
- `other_types: ["<other_type>", ...]`
- Endless-only: `speed: { start_px_per_sec, accel_px_per_min, max_px_per_sec }`
- Classic-only: `classic: { rows_total: int (>0), advance_animation_ms: int (>=0, default 160) }`
- `hit_window_ms: { good }` — only the “good” window is used; any `perfect` value is ignored if present
- `assets_root: "assets"`
- `supported_formats: ["png", "jpg"]`
- `controls: { keys: ["<k0>","<k1>","<k2>","<k3>"] }` — pygame key names, order defines lanes left→right; must be unique and length must equal `lanes`.

Example (endless):

```json
{
  "lanes": 4,
  "mode": "endless",
  "target_type": "aiko",
  "other_types": ["pikachu", "sesame"],
  "speed": { "start_px_per_sec": 400, "accel_px_per_min": 250, "max_px_per_sec": 1200 },
  "hit_window_ms": { "good": 120 },
  "assets_root": "assets",
  "supported_formats": ["png", "jpg"],
  "controls": { "keys": ["a", "s", "d", "f"] }
}
```

Example (classic):

```json
{
  "lanes": 4,
  "mode": "classic",
  "target_type": "aiko",
  "other_types": ["pikachu", "sesame"],
  "classic": { "rows_total": 60, "advance_animation_ms": 160 },
  "hit_window_ms": { "good": 120 },
  "assets_root": "assets",
  "supported_formats": ["png", "jpg"],
  "controls": { "keys": ["a", "s", "d", "f"] }
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
  - Endless (`Game`):
    - State: score, elapsed_time, `current_speed`, tile list, lane geometry, hit line Y.
    - Update per frame: increase speed linearly and move tiles; miss detection if a target tile crosses the hit line; spawn new rows when spacing threshold is met.
  - Classic (`ClassicGame`):
    - Pre-generate exactly `rows_total` rows; no autonomous scrolling.
    - Timer starts on first valid user input and stops immediately after the final correct hit.
    - On correct hit: animate a one-row advance over `advance_animation_ms` (or instant if 0); inputs ignored during animation.
    - On wrong tap: immediate game over. When all rows are cleared: finished state.

- Input handling (configurable keys)
  - Map key to lane index (0..3).
  - On keydown, find the nearest tile in that lane intersecting the hit line within the `good` window.
  - Endless: if tile exists and `type_name == target_type`: mark `hit`, score += 1; otherwise: game over. Misses end when target crosses the hit line.
  - Classic: if tile exists and `type_name == target_type`: mark `hit` and advance; otherwise: game over.

- HUD (`hud.py`)
  - Endless: draw current `target_type` thumbnail, `score`, and a `timer` bar (based on elapsed run time).
  - Classic: draw target thumbnail, `Rows: cleared/total`, and a prominent mm:ss.ms timer (`render_hud_classic`).

### Geometry and rendering

- Suggested base resolution: 480×800 (portrait). Compute `lane_width = window_width / lanes`.
- Tile height proportional to window height (e.g., enough for ~4 rows visible).
- Hit line near bottom (≈ 88% of height). Draw as a thin guide line.
- Draw order: background → tiles → hit effects → HUD.

### Hit window

- Use `hit_window_ms.good`. Convert to pixels with current speed for proximity checks, or compare times by extrapolating crossing time to the hit line.

 

### Performance considerations

- Preload and pre-scale all images at startup; avoid per-frame scaling and disk I/O.
- Use integer-aligned blits when possible; minimize surface conversions in the loop.

### Difficulty ramp

- Endless only: linear acceleration over time, capped at `max_px_per_sec`.

### Game over and completion

- Endless: Full-screen overlay showing final score and a brief message; allow restart or quit.
- Classic: Finished overlay with final time; wrong tap shows game over with elapsed time; allow restart or quit.

### Edge cases

- `other_types` may be empty; rows still spawn exactly one `target_type` tile.
- Missing or empty asset folders: fail clearly.
- Mixed image sizes/aspect ratios: maintain aspect with center-crop or letterbox.

### Milestones

1. Project scaffolding, config loader, constants.
2. AssetManager with preload/scale.
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


