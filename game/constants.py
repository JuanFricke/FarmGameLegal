import os

SCREEN_W = 1024
SCREEN_H = 768
FPS = 60

TILE_SIZE = 64

# Farm grid dimensions (tiles)
GRID_COLS = 10
GRID_ROWS = 8

# Panel widths/heights
HUD_H = 48
FARM_W = GRID_COLS * TILE_SIZE   # 640
CODE_PANEL_W = SCREEN_W - FARM_W  # 384

# Colors
SKY_COLOR       = (135, 206, 235)
GRASS_COLOR     = (74,  124, 89)
SOIL_COLOR      = (101, 67,  33)
SOIL_TILLED     = (139, 94,  48)
PANEL_BG        = (30,  30,  40)
PANEL_BORDER    = (80,  80, 110)
TEXT_COLOR      = (220, 220, 240)
TEXT_DIM        = (130, 130, 160)
HINT_COLOR      = (255, 180,  60)
ERROR_COLOR     = (255,  80,  80)
SUCCESS_COLOR   = (80,  220, 120)
CURSOR_COLOR    = (255, 255, 255)
HUD_BG          = (20,  20,  30)
HIGHLIGHT_COLOR = (255, 220,  80)

# Noto Color Emoji font path
NOTO_EMOJI_FONT = "/usr/share/fonts/google-noto-color-emoji-fonts/NotoColorEmoji.ttf"

# Emoji used in the game
EMOJI_PLAYER    = "🧑‍🌾"
EMOJI_SEED      = "🌱"
EMOJI_SPROUT    = "🌿"
EMOJI_HARVEST   = "✨"

EMOJI_POTATO    = "🥔"
EMOJI_CARROT    = "🥕"
EMOJI_PUMPKIN   = "🎃"
EMOJI_CORN      = "🌽"
