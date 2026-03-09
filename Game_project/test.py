import pygame

# --- Configuration & Settings ---
WIDTH, HEIGHT = 800, 600
FPS = 60
WHITE = (255, 255, 255)
RED = (200, 0, 0)
GREEN = (34, 139, 34)
GRAVITY = 0.8
JUMP_STRENGTH = -16
SPEED = 5

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((40, 40))
        self.image.fill(RED)
        self.rect = self.image.get_rect(center=(100, HEIGHT - 100))
        self.vel_y = 0
        self.on_ground = False

    def update(self, platforms):
        # Movement
        keys = pygame.key.get_pressed()
        #Move left
        if keys[pygame.K_a]:
            self.rect.x -= SPEED
        # Move right
        if keys[pygame.K_d]:
            self.rect.x += SPEED

        # Jump Logic
        if keys[pygame.K_SPACE] and self.on_ground:
            self.vel_y = JUMP_STRENGTH
            self.on_ground = False

        # Apply Gravity
        self.vel_y += GRAVITY
        self.rect.y += self.vel_y

        # Basic Collision Check
        self.on_ground = False
        for plat in platforms:
            if self.rect.colliderect(plat.rect):
                if self.vel_y > 0:  # Falling
                    self.rect.bottom = plat.rect.top
                    self.vel_y = 0
                    self.on_ground = True


class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h):
        super().__init__()
        self.image = pygame.Surface((w, h))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect(topleft=(x, y))


# --- Main Game Loop ---
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Roguelike Side-Scroller Prototype")
    clock = pygame.time.Clock()

    # Groups
    all_sprites = pygame.sprite.Group()
    platforms = pygame.sprite.Group()

    # Create Player & Floor
    player = Player()
    floor = Platform(0, HEIGHT - 50, WIDTH, 50)

    all_sprites.add(player, floor)
    platforms.add(floor)

    running = True
    while running:
        # 1. Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # 2. Logic / Update
        all_sprites.update(platforms)

        # 3. Rendering
        screen.fill(WHITE)
        all_sprites.draw(screen)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()