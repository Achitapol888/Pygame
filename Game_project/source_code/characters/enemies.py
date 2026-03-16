import pygame
from source_code.settings import RED, WHITE, GAME_WIDTH
import random, math

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, is_glitch=False):
        super().__init__()
        self.width = 48
        self.height = 40
        self.image = pygame.Surface((self.width, self.height))

        # If it's a glitch enemy, make it look like a wireframe
        self.is_glitch = is_glitch
        self.color = (255, 0, 0) if not is_glitch else (0, 255, 255)  # Cyan for glitch
        self.image.fill(self.color)

        self.rect = self.image.get_rect(topleft=(x, y))

        # Add this just in case something tries to check for interactions
        self.interact_rect = self.rect


        # Stats
        self.hp = 100
        self.max_hp = 100
        self.is_alive = True
        self.flash_timer = 0  # Added to make the damage flash visible

    def take_damage(self, amount):
        if self.is_alive:
            self.hp -= amount
            self.flash_timer = 5  # Flash for 5 frames

            if self.hp <= 0:
                self.die()

    def die(self):
        self.is_alive = False
        self.kill()
        print("Enemy defeated!")

    def update(self):
        if self.is_alive:
            # Handle Damage Flash
            if self.flash_timer > 0:
                self.image.fill(WHITE)
                self.flash_timer -= 1
            else:
                self.image.fill(RED)

            # Draw health bar (now shorter to match new width)
            health_ratio = max(0, self.hp / self.max_hp)
            health_width = int(health_ratio * self.width)
            pygame.draw.rect(self.image, (0, 255, 0), (0, 0, health_width, 5))

    def draw_debug(self, surface):
        pygame.draw.rect(surface, (255, 255, 0), self.rect, 1)


class SlimeEnemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()

        # --- ADJUSTABLE SETTINGS ---
        self.width = 54
        self.height = 96  # Squashed look
        self.base_anim_delay = 100
        # ---------------------------

        self.frames = []
        for i in range(1, 4):  # Using your 3 provided glitch frames
            img = pygame.image.load(f"Game_project/assets/sprites/Glitch/No_texture{i}.png").convert_alpha()
            self.frames.append(pygame.transform.scale(img, (self.width, self.height)))

        self.frame_index = 0
        self.image = self.frames[self.frame_index]

        # Use midbottom to anchor it to the floor (y is the floor top)
        self.rect = self.image.get_rect(midbottom=(x, y))
        self.interact_rect = self.rect

        # Movement
        self.speed = random.uniform(1.2, 1.8)
        self.direction = 1
        self.walk_distance = 150
        self.start_x = x

        # Stats
        self.hp = 50
        self.contact_damage = 10
        self.is_alive = True
        self.flash_timer = 0
        self.flash_duration = 10  # Number of frames to stay red

        self.last_anim_update = pygame.time.get_ticks()
        # Randomized delay makes it look "glitchy/unstable" rather than robotic
        self.current_delay = self.base_anim_delay + random.randint(-20, 50)

    def update(self, player=None):
        if not self.is_alive: return

        # 1. MOVE
        self.rect.x += self.speed * self.direction

        # 2. SCREEN BOUNDARIES (The "Invisible Walls")
        if self.rect.left < 0:
            self.rect.left = 0
            self.direction = 1  # Force go right
        elif self.rect.right > GAME_WIDTH:  # Replace with GAME_WIDTH if imported
            self.rect.right = GAME_WIDTH
            self.direction = -1  # Force go left

        # 3. PATROL BOUNDARIES
        if abs(self.rect.x - self.start_x) > self.walk_distance:
            self.direction *= -1

        # Animation logic with variable timing
        # 2. Animation Logic
        now = pygame.time.get_ticks()
        if now - self.last_anim_update > self.current_delay:
            self.last_anim_update = now
            self.frame_index = (self.frame_index + 1) % len(self.frames)
            # Create a fresh copy of the frame to avoid permanent tinting
            self.image = self.frames[self.frame_index].copy()

        # 3. Red Tint Logic
        if self.flash_timer > 0:
            self.flash_timer -= 1
            # Apply the red tint using BLEND_RGB_MULT
            # (255, 100, 100) multiplies the Red channel by 1.0 and reduces G/B
            tint_surface = pygame.Surface(self.image.get_size(), pygame.SRCALPHA)
            tint_surface.fill((255, 50, 50)) # Bright Red tint
            self.image.blit(tint_surface, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

        # 4. Contact Damage
        if player and self.rect.colliderect(player.rect):
            player.take_damage(self.contact_damage)

    def take_damage(self, amount):
        if self.is_alive:
            self.hp -= amount
            self.flash_timer = self.flash_duration  # Start the red tint
            if self.hp <= 0:
                self.die()

    def die(self):
        self.is_alive = False
        self.kill()


class BossMinion(pygame.sprite.Sprite):
    def __init__(self, x, y, minion_type):
        super().__init__()
        self.minion_type = minion_type

        # 1. LOAD ANIMATION FRAMES
        self.frames = []
        if minion_type == 1:
            for i in range(1, 5):  # boss_trop_1_1 to 4
                img = pygame.image.load(f"Game_project/assets/sprites/boss/boss_trop_1_{i}.png").convert_alpha()
                self.frames.append(img)
            self.hp = 30
        else:
            for i in range(1, 3):  # boss_trop_2_1 to 2
                img = pygame.image.load(f"Game_project/assets/sprites/boss/boss_trop_2_{i}.png").convert_alpha()
                self.frames.append(img)
            self.hp = 50

        self.image = self.frames[0]
        self.rect = self.image.get_rect(midbottom=(x, y + 10))
        self.pos_x = float(self.rect.x)
        self.speed = random.uniform(1.0, 2.0)

        # Animation State
        self.frame_index = 0
        self.anim_speed = 0.15

        # Damage cooldown
        self.last_attack_time = 0
        self.attack_cooldown = 1000  # 1 second

    def take_damage(self, amount):
        self.hp -= amount
        if self.hp <= 0: self.kill()

    def update(self, player=None):
        if not player: return

        # 2. ANIMATION LOGIC
        self.frame_index += self.anim_speed
        if self.frame_index >= len(self.frames):
            self.frame_index = 0

        # Flip image based on direction
        raw_img = self.frames[int(self.frame_index)]
        if self.rect.centerx < player.rect.centerx:
            self.image = pygame.transform.flip(raw_img, True, False)  # Face Right
            self.pos_x += self.speed
        else:
            self.image = raw_img  # Face Left
            self.pos_x -= self.speed

        self.rect.x = int(self.pos_x)

        # 3. DAMAGE PLAYER LOGIC
        if self.rect.colliderect(player.rect):
            now = pygame.time.get_ticks()
            if now - self.last_attack_time > self.attack_cooldown:
                player.take_damage(10)  # Adjust damage as needed
                self.last_attack_time = now


class Boss(pygame.sprite.Sprite):
    def __init__(self, x, ground_y):
        super().__init__()
        original_img = pygame.image.load("Game_project/assets/sprites/boss/boss.png").convert_alpha()

        # 1. REDUCE SIZE (e.g., 0.7 = 70% of original size)
        scale_factor = 0.6
        new_size = (int(original_img.get_width() * scale_factor),
                    int(original_img.get_height() * scale_factor))
        self.image = pygame.transform.scale(original_img, new_size)

        self.hover_timer = 0
        self.ground_y = ground_y
        self.flight_y = ground_y - 200
        self.rect = self.image.get_rect(midbottom=(x, self.flight_y))

        self.hp = 100
        self.state = "FLYING"
        self.spawn_timer = 120
        self.active_minions = []

    def spawn_minions(self, enemy_group):
        print("Boss: Spawning Minions!")
        self.active_minions.clear()

        # Spawn 2 to 3 random minions
        for _ in range(random.randint(2, 3)):
            spawn_x = random.randint(200, 600)
            m_type = random.choice([1, 2])
            minion = BossMinion(spawn_x, self.ground_y, m_type)

            enemy_group.add(minion)  # Add to the game world
            self.active_minions.append(minion)  # Boss remembers them

    def update(self, player, enemy_group):
        # 1. FLYING: Floating high, preparing to spawn

        if self.state == "FLYING" or self.state == "WAITING":
            self.hover_timer += 0.05
            # Offset the y by a sine wave (-10 to +10 pixels)
            hover_offset = math.sin(self.hover_timer) * 10
            self.rect.y = self.flight_y + hover_offset

        if self.state == "FLYING":
            self.spawn_timer -= 1
            if self.spawn_timer <= 0:
                self.spawn_minions(enemy_group)
                self.state = "WAITING"

        # 2. WAITING: Watching the player fight minions
        elif self.state == "WAITING":
            # Check if all minions are dead
            # .alive() checks if the sprite is still in any groups
            alive_minions = [m for m in self.active_minions if m.alive()]

            if len(alive_minions) == 0:
                print("Boss: Shield broken! Falling!")
                self.state = "FALLING"

        # 3. FALLING: Crashing to the ground
        elif self.state == "FALLING":
            self.rect.y += 8  # Drop fast
            if self.rect.bottom >= self.ground_y:
                self.rect.bottom = self.ground_y
                self.state = "STUNNED"
                self.stun_timer = 300  # Stunned for 5 seconds (at 60fps)
                print("Boss is VULNERABLE!")

        # 4. STUNNED: On the ground, player can attack
        elif self.state == "STUNNED":
            self.stun_timer -= 1
            # Add a slight shake/color change effect here if you want!
            if self.stun_timer <= 0:
                self.state = "RISING"

        # 5. RISING: Going back to the sky
        elif self.state == "RISING":
            self.rect.y -= 4
            if self.rect.y <= self.flight_y:
                self.rect.y = self.flight_y
                self.state = "FLYING"
                self.spawn_timer = 180  # Reset spawn timer