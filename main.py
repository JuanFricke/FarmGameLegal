"""
Farm Code — main entry point.
Run with:  uv run main.py
"""
from __future__ import annotations
import subprocess
import pygame

from game.constants import (
    SCREEN_W, SCREEN_H, FPS,
    HUD_H, FARM_W, TILE_SIZE,
    SKY_COLOR, GRASS_COLOR,
    SUCCESS_COLOR, ERROR_COLOR, HINT_COLOR,
)
from game.tilemap import Tilemap
from game.player import Player
from game.crop import Crop, CropType, GrowthStage
from game.challenges import ALL_CHALLENGES, Challenge
from game.sandbox import run_challenge
from game.code_panel import ResultsPanel, PanelState
from game.particles import ParticleSystem
from game.hud import HUD
from game.external_editor import EditorManager
from game import plot_store


# ---------------------------------------------------------------------------
# Phase data
# ---------------------------------------------------------------------------

PHASE_NAMES = {
    CropType.POTATO:  "Fase 1 - Batata",
    CropType.CARROT:  "Fase 2 - Cenoura",
    CropType.PUMPKIN: "Fase 3 - Abobora",
    CropType.CORN:    "Fase 4 - Milho (Bonus)",
}

CHALLENGE_BY_TYPE: dict[CropType, Challenge] = {
    c.crop_type: c for c in ALL_CHALLENGES
}

UNLOCK_ORDER = [CropType.POTATO, CropType.CARROT, CropType.PUMPKIN, CropType.CORN]


# ---------------------------------------------------------------------------
# Game
# ---------------------------------------------------------------------------

class Game:
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("Farm Code")
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        self.clock  = pygame.time.Clock()

        self.tilemap   = Tilemap()
        self.player    = Player(self.tilemap)
        self.panel     = ResultsPanel()
        self.particles = ParticleSystem()
        self.hud       = HUD()

        self._crops: list[Crop] = []
        self._unlocked_idx = 0
        self._solved: set[CropType] = set()

        self._editors = EditorManager()

        # Sync panel with initial editor state
        self.panel.editor_name = self._editors.current
        self.panel.all_editors = self._editors.all

        # Editor subprocess (None when no editor is open)
        self._editor_proc: subprocess.Popen | None = None
        self._editing_crop: Crop | None = None

        self.hud.set_phase(PHASE_NAMES[UNLOCK_ORDER[0]])
        self.running = True

    # ------------------------------------------------------------------
    # Main loop
    # ------------------------------------------------------------------

    def run(self) -> None:
        while self.running:
            dt = self.clock.tick(FPS)
            self._poll_editor()
            self._handle_events()
            self._update(dt)
            self._draw()
        pygame.quit()

    # ------------------------------------------------------------------
    # External editor polling
    # ------------------------------------------------------------------

    def _poll_editor(self) -> None:
        """Check if the external editor process has exited."""
        if self._editor_proc is None:
            return
        if self._editor_proc.poll() is None:
            return  # still open

        # Editor was closed — read file and run tests
        proc = self._editor_proc
        self._editor_proc = None
        crop = self._editing_crop
        self._editing_crop = None

        if crop is None:
            return

        tile = crop.tile
        code = plot_store.load(tile.col, tile.row, fallback="")
        challenge = CHALLENGE_BY_TYPE.get(crop.crop_type)
        if not challenge:
            return

        result = run_challenge(challenge, code)
        self.panel.show_results(result, function_name=challenge.function_name)

        if result.passed:
            self.hud.add_score(result.score)
            crop.advance_to_mature()
            self.hud.flash(
                f"Correto! +{result.score} pts - pressione E para colher!",
                SUCCESS_COLOR,
            )
        else:
            crop.advance_to_sprout()
            self.hud.flash("Alguns testes falharam. Veja o painel.", ERROR_COLOR)

    # ------------------------------------------------------------------
    # Events
    # ------------------------------------------------------------------

    def _handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False

                elif event.key == pygame.K_e:
                    if self._editor_proc is not None:
                        self.hud.flash("Editor ja esta aberto!", HINT_COLOR)
                    else:
                        self._interact()

                elif event.key == pygame.K_SPACE:
                    if self._editor_proc is None:
                        name = self._editors.cycle()
                        self.hud.flash(f"Editor: {name}", HINT_COLOR, 90)
                        # Update panel display immediately
                        self.panel.editor_name  = name
                        self.panel.all_editors  = self._editors.all

    # ------------------------------------------------------------------
    # Interaction
    # ------------------------------------------------------------------

    def _interact(self) -> None:
        tile = self.player.nearest_soil_tile()
        if tile is None:
            self.hud.flash("Aproxime-se de um canteiro de solo.", HINT_COLOR)
            return

        if tile.crop is not None:
            crop = tile.crop
            if crop.is_harvestable:
                self._harvest(crop, tile)
                return
            # Crop exists but not harvestable — open editor on its file
            self._open_editor_for(crop)
        else:
            # Empty soil — plant and open editor
            crop_type = UNLOCK_ORDER[min(self._unlocked_idx, len(UNLOCK_ORDER) - 1)]
            crop = Crop(crop_type, tile)
            tile.crop = crop
            self._crops.append(crop)
            self._open_editor_for(crop)

    def _open_editor_for(self, crop: Crop) -> None:
        challenge = CHALLENGE_BY_TYPE.get(crop.crop_type)
        if not challenge:
            return

        tile = crop.tile
        filepath = plot_store.init(tile.col, tile.row, challenge.starter_code)

        self.panel.show_editing(
            title=challenge.title,
            desc=challenge.description,
            function_name=challenge.function_name,
            editor=self._editors.current,
            all_editors=self._editors.all,
            path=str(filepath),
        )

        try:
            self._editor_proc  = self._editors.open(str(filepath))
            self._editing_crop = crop
        except RuntimeError as exc:
            self.hud.flash(str(exc)[:60], ERROR_COLOR, 300)
            self.panel.show_idle()

    def _harvest(self, crop: Crop, tile) -> None:
        crop.harvest()
        cx = tile.col * TILE_SIZE + TILE_SIZE // 2
        cy = HUD_H + tile.row * TILE_SIZE + TILE_SIZE // 2
        self.particles.burst(cx, cy)
        self.hud.flash("Colhido!", SUCCESS_COLOR)
        self.panel.show_idle()

        if crop.crop_type not in self._solved:
            self._solved.add(crop.crop_type)
            next_idx = self._unlocked_idx + 1
            if next_idx < len(UNLOCK_ORDER):
                self._unlocked_idx = next_idx
                nxt = UNLOCK_ORDER[next_idx]
                self.hud.set_phase(PHASE_NAMES[nxt])
                self.hud.flash(f"Nova fase: {PHASE_NAMES[nxt]}", HINT_COLOR, 240)
            else:
                self.hud.flash("Parabens! Voce completou todas as fases!", SUCCESS_COLOR, 300)

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------

    def _update(self, dt_ms: int) -> None:
        # Allow movement only when editor is not open
        if self._editor_proc is None and self.panel.state != PanelState.EDITING:
            keys = pygame.key.get_pressed()
            self.player.handle_movement(keys)

        # Highlight nearest interactable tile
        self.tilemap.clear_highlights()
        tile = self.player.nearest_soil_tile()
        if tile:
            tile.highlighted = True

        self.hud.update()
        self.particles.update()

        # Remove finished harvest animations, clear tile
        done = [c for c in self._crops if c.is_done]
        for crop in done:
            crop.tile.crop = None
            self._crops.remove(crop)

    # ------------------------------------------------------------------
    # Draw
    # ------------------------------------------------------------------

    def _draw(self) -> None:
        self.screen.fill(SKY_COLOR)

        pygame.draw.rect(
            self.screen, GRASS_COLOR,
            (0, HUD_H, FARM_W, SCREEN_H - HUD_H),
        )

        self.tilemap.draw(self.screen)

        for crop in self._crops:
            crop.draw(self.screen)

        self.player.draw(self.screen)
        self.particles.draw(self.screen)
        self.panel.draw(self.screen)
        self.hud.draw(self.screen)

        pygame.display.flip()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    Game().run()
