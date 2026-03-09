# source_code/states/game_play.py
import pygame
from source_code.states.base_state import BaseState
from source_code.settings import WHITE, GAME_HEIGHT, GAME_WIDTH, BLACK, BAR_HEIGHT
from source_code.characters.player import Player
from source_code.world import Platform
from source_code.systems.ui import HUD


class GameplayState(BaseState):
    def __init__(self, engine):
        super().__init__(engine)
        self.all_sprites = pygame.sprite.Group()
        self.platforms = pygame.sprite.Group()

        self.player = Player()
        self.all_sprites.add(self.player)

        # 1. Calculate floor position ONCE here
        floor_y = GAME_HEIGHT - BAR_HEIGHT - 20

        # 2. Create the platform using that position
        floor = Platform(0, floor_y, GAME_WIDTH, 20)

        self.all_sprites.add(floor)
        self.platforms.add(floor)

        self.hud = HUD(self.player)

    def handle_events(self, events):
        # 1. Let the player handle inventory/movement keys ONCE
        self.player.handle_input(events)

        # 2. Handle state-specific keys (like Esc to menu)
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.next_state = "MENU"

    def update(self, dt):
        self.all_sprites.update(self.platforms)

    def draw(self, surface):
        surface.fill(WHITE)

        self.all_sprites.draw(surface)

        self.hud.draw(surface)