# source_code/systems/ui.py
import pygame
from source_code.settings import WHITE, RED, BLACK, BAR_HEIGHT


class HUD:
    def __init__(self, player):
        self.player = player
        # Colors for our bars
        self.BLUE = (0, 100, 255)
        self.PINK = (255, 150, 150)  # For the Sanity icon/brain
        self.DARK_GREY = (40, 40, 40)

    def draw(self, surface):
        # 1. Draw Black cinematic bars first
        pygame.draw.rect(surface, BLACK, (0, 0, surface.get_width(), BAR_HEIGHT))
        pygame.draw.rect(surface, BLACK, (0, surface.get_height() - BAR_HEIGHT, surface.get_width(), BAR_HEIGHT))

        # 2. Draw the Health and Stamina bars + Sanity
        self.draw_stats(surface)

        # 3. Draw the inventory (your previous code)
        # self.draw_hotbar(surface)

    def draw_stats(self, surface):
        # Position variables
        margin_x = 15
        margin_y = 12

        # --- SANITY CIRCLE ---
        # Draw the circle to the left of the bars
        circle_center = (margin_x + 15, BAR_HEIGHT // 2)
        pygame.draw.circle(surface, WHITE, circle_center, 18, 2)  # Outer ring
        pygame.draw.circle(surface, self.PINK, circle_center, 14)  # Inner brain-color circle

        # Offset the bars to the right of the circle
        bar_start_x = margin_x + 45

        # --- HP BAR ---
        hp_rect = pygame.Rect(bar_start_x, margin_y, 100, 12)
        pygame.draw.rect(surface, self.DARK_GREY, hp_rect)  # Background
        # Logic: (current / max) * width
        pygame.draw.rect(surface, RED, (bar_start_x, margin_y, 100, 12))
        pygame.draw.rect(surface, WHITE, hp_rect, 1)  # Border

        # --- STAMINA BAR (Under HP) ---
        stamina_y = margin_y + 16  # Small gap below HP
        stamina_rect = pygame.Rect(bar_start_x, stamina_y, 80, 8)  # Slightly shorter/thinner
        pygame.draw.rect(surface, self.DARK_GREY, stamina_rect)  # Background
        pygame.draw.rect(surface, self.BLUE, (bar_start_x, stamina_y, 80, 8))
        pygame.draw.rect(surface, WHITE, stamina_rect, 1)  # Border