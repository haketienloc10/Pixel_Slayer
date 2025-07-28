from pathlib import Path

# --- Constants ---
LEVEL_2_THRESHOLD: int = 50
ASSET_DIR: Path = Path("assets")

# --- Sprite Definitions ---
SPRITES: dict[str, dict[int, dict[str, str]]] = {
    "character": {
        1: {"idle": "warrior_lv1_idle.png", "attack": "warrior_lv1_attack.png"},
        2: {"idle": "warrior_lv2_idle.png", "attack": "warrior_lv2_attack.png"},
    },
    "monster": {
        1: {"idle": "monster_lv1_idle.png", "hurt": "monster_lv1_hurt.png"},
        2: {"idle": "monster_lv2_idle.png", "hurt": "monster_lv2_hurt.png"},
    },
}