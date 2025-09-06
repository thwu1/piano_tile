## Piano Tiles with Image Types (n-type version)

This variant of Piano Tiles replaces black/white tiles with images from configurable categories (types), such as `cat`, `dog`, `bird`, etc. The player must tap only the tiles belonging to the current target type(s) while avoiding all others, as tiles scroll down the screen.

### Assets and setup

- **Types and folders**: Under `/assets`, each `/assets/{type_name}` defines a tile type named `{type_name}`. For example:
  - `assets/cat/` → type "cat"
  - `assets/dog/` → type "dog"
  - `assets/bird/` → type "bird"
- **Supported formats**: PNG/JPG (no GIF).
- **Sampling rule**: When a tile of a given type is spawned, its image is sampled uniformly at random from that type’s folder.
- **Preprocessing**: Images are preloaded, scaled to tile size, and optionally center-cropped or letterboxed to preserve aspect ratio.

### Gameplay and rules

- **Lanes**: 4 lanes.
- **Scrolling**: Tiles spawn at the top and scroll downward. Each row can contain one or more tiles.
- **Target type (Endless mode)**: A fixed `target_type` is configured at start. Tap only tiles of this type; tapping any other type or missing the `target_type` ends the run.
- **Failure conditions**:
  - A target tile passes the hit line without being tapped.
  - You tap a non-target tile.

### Tile generation

- **Row solvency**: Always spawn exactly one tile of the `target_type` per row.
- **Other types**: Fill remaining lanes in the row with tiles from other types chosen uniformly at random (no additional constraints).

### Scoring

- **Base scoring**: +1 per correct tap. No combos, multipliers, or accuracy bonuses.

### Input and controls

- **Touch/mouse**: Tap/click a tile when it reaches the hit line.
- **Keyboard**: Four lanes mapped to `H J K L` (left→right).
- **Hit detection**: A tap within the lane and within the vertical hit window counts as a hit if the tile type is currently targeted.

### UI and feedback

- **HUD**:
  - Current target type(s) with small preview/icon.
  - Score.
  - Timer/progress bar.
- **Visual feedback**:
  - On hit: brief glow/pulse and removal of the tile.
  - On miss/wrong: red flash, shake, or vignette; immediate stop in classic mode.

### Configuration

- **Directory layout**: `assets/<type_name>/*` image files per type.
- **Runtime config**: lanes, base speed, acceleration, max speed, hit windows, base scoring only, `target_type` (fixed), keyboard mapping `H J K L`.

Example config (JSON):

```json
{
  "lanes": 4,
  "mode": "endless",
  "target_type": "cat",
  "other_types": ["dog", "bird"],
  "speed": { "start_px_per_sec": 400, "accel_px_per_min": 250, "max_px_per_sec": 1200 },
  "hit_window_ms": { "good": 120, "perfect": 60 },
  "scoring": { "base": 1 },
  "assets_root": "assets",
  "supported_formats": ["png", "jpg"],
  "controls": { "keys": ["H", "J", "K", "L"] }
}
```

### Difficulty ramp

- **Speed increase**: Scroll speed gradually increases over time.
- **Max speed**: Speed is capped at a configured maximum to keep the game fair.

### Performance and robustness

- **Preloading and caching**: Load/scale images at start; keep per-type pools in memory to avoid frame drops.
- **Resolution independence**: Tile size scales to window; letterbox/pillarbox to maintain aspect ratio.

### End-of-run

- **Game over screen**: Show final score and indicate which type (if any) was missed.


