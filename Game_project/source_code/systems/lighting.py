import pygame


class LightingSystem:
    def __init__(self, screen_width, screen_height):
        # The surface that covers the screen in darkness
        self.mask = pygame.Surface((screen_width, screen_height))
        self.ambient_color = (50, 50, 50)  # Very dark blue/black

        # Create the flashlight glow (200px radius)
        self.light_radius = 200
        self.light_surface = self.create_light_gradient(self.light_radius, (255, 255, 230))

    def create_light_gradient(self, radius, color):
        """Creates a soft, circular glow that fades out."""
        surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        for i in range(radius, 0, -2):
            alpha = int(180 * (i / radius) ** 2)  # Adjust 180 for brightness
            pygame.draw.circle(surface, (*color, alpha), (radius, radius), i)
        return surface

    def update_and_draw(self, screen, player_rect):
        # 1. Reset the mask to darkness
        self.mask.fill(self.ambient_color)

        # 2. Draw the flashlight at the player's position
        # Offset by radius to center it on the player
        light_pos = (player_rect.centerx - self.light_radius,
                     player_rect.centery - self.light_radius)

        self.mask.blit(self.light_surface, light_pos, special_flags=pygame.BLEND_RGBA_ADD)

        # 3. Blit the mask onto the main screen using MULTIPLY
        # This makes the dark areas look deep and the light areas look natural
        screen.blit(self.mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)