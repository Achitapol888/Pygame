# source_code/engine.py
import pygame
from source_code.settings import *
from source_code.states.menu import MenuState
from source_code.states.game_play import GameplayState


class Engine:
    def __init__(self):
        pygame.init()
        if USE_FULLSCREEN:
            self.window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.FULLSCREEN)
        else:
            self.window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)
        self.display_surface = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True

        # State Dictionary
        self.states = {
            "MENU": MenuState(self),
            "GAMEPLAY": GameplayState(self)
        }
        self.active_state = self.states["MENU"]

    def flip_state(self):
        """Switches the active state if requested."""
        if self.active_state.next_state:
            # Reset the next_state trigger before switching
            target = self.active_state.next_state
            self.active_state.next_state = None
            self.active_state = self.states[target]

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS)
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False

            # State Logic
            self.active_state.handle_events(events)
            self.active_state.update(dt)
            self.flip_state()

            # Rendering
            self.display_surface.fill(BLACK)  # Clear internal surface
            self.active_state.draw(self.display_surface)

            scaled = pygame.transform.scale(self.display_surface, (WINDOW_WIDTH, WINDOW_HEIGHT))
            self.window.blit(scaled, (0, 0))
            pygame.display.flip()