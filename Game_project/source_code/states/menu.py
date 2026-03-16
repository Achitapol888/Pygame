import pygame
from source_code.states.base_state import BaseState
from source_code.settings import WHITE, BLACK, GAME_WIDTH, GAME_HEIGHT

class MenuState(BaseState):
    def __init__(self, engine):
        super().__init__(engine)
        self.font = pygame.font.SysFont("Arial", 32)

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:  # Press 'P' to play
                    self.next_state = "GAMEPLAY"
                if event.key == pygame.K_q:  # Press 'Q' to quit
                    self.engine.running = False

    def draw(self, surface):
        surface.fill(BLACK)
        title = self.font.render("The Elevator", True, WHITE)
        instruction = self.font.render("Press 'P' to Play or 'Q' to Quit", True, WHITE)

        surface.blit(title, (GAME_WIDTH // 2 - title.get_width() // 2, 100))
        surface.blit(instruction, (GAME_WIDTH // 2 - instruction.get_width() // 2, 200))