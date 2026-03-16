# source_code/engine.py
import pygame
from source_code.settings import *
from source_code.states.menu import MenuState
from source_code.states.game_play import GameplayState

class Engine:
    def __init__(self):
        pygame.init()
        # Initial Window Setup
        self.current_win_w = WINDOW_WIDTH
        self.current_win_h = WINDOW_HEIGHT

        flags = pygame.RESIZABLE
        if USE_FULLSCREEN:
            flags |= pygame.FULLSCREEN

        # Create window once
        self.window = pygame.display.set_mode((self.current_win_w, self.current_win_h), flags)

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
            target = self.active_state.next_state
            self.active_state.next_state = None
            self.active_state = self.states[target]

    def render_to_window(self):
        """Scales the internal display to the window with Letterboxing."""
        # Calculate aspect ratios
        window_ratio = self.current_win_w / self.current_win_h
        game_ratio = GAME_WIDTH / GAME_HEIGHT

        if window_ratio > game_ratio:
            # Window is too wide (bars on sides)
            scale_height = self.current_win_h
            scale_width = int(scale_height * game_ratio)
        else:
            # Window is too tall (bars on top/bottom)
            scale_width = self.current_win_w
            scale_height = int(scale_width / game_ratio)

        # Scale and Center
        scaled_surf = pygame.transform.scale(self.display_surface, (scale_width, scale_height))
        pos_x = (self.current_win_w - scale_width) // 2
        pos_y = (self.current_win_h - scale_height) // 2

        self.window.fill(BLACK)
        self.window.blit(scaled_surf, (pos_x, pos_y))

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS)
            events = pygame.event.get()

            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False

                # Handle resizing
                if event.type == pygame.VIDEORESIZE:
                    self.current_win_w, self.current_win_h = event.w, event.h
                    # Update window size without losing flags
                    self.window = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)

                # Alt + Enter Toggle
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN and (pygame.key.get_mods() & pygame.KMOD_ALT):
                        pygame.display.toggle_fullscreen()

            # Logic
            self.active_state.handle_events(events)
            self.active_state.update(dt)
            self.flip_state()  # This now exists!

            # Rendering
            self.display_surface.fill(BLACK)
            self.active_state.draw(self.display_surface)

            # Draw to window
            self.render_to_window()
            pygame.display.flip()

    def get_game_mouse_pos(self):
        """Converts real window mouse position to game world coordinates (640x360)."""
        win_x, win_y = pygame.mouse.get_pos()

        # 1. Calculate the same scaling factors used in render_to_window
        window_ratio = self.current_win_w / self.current_win_h
        game_ratio = GAME_WIDTH / GAME_HEIGHT

        if window_ratio > game_ratio:
            scale_height = self.current_win_h
            scale_width = int(scale_height * game_ratio)
        else:
            scale_width = self.current_win_w
            scale_height = int(scale_width / game_ratio)

        # 2. Calculate offsets (the black bars)
        offset_x = (self.current_win_w - scale_width) // 2
        offset_y = (self.current_win_h - scale_height) // 2

        # 3. Translate and Scale the coordinates
        # Subtract the offset, then multiply by the ratio of internal/scaled size
        try:
            game_x = (win_x - offset_x) * (GAME_WIDTH / scale_width)
            game_y = (win_y - offset_y) * (GAME_HEIGHT / scale_height)
        except ZeroDivisionError:
            return 0, 0

        return game_x, game_y