import pygame
from source_code.settings import *
from source_code.systems.inventory import Inventory
from source_code.characters.enemies import Enemy, Boss

def load_anim(path, size):
    img = pygame.image.load(path).convert_alpha()
    return pygame.transform.scale(img, size)

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.size = (48, 64)
        self.y_offset = 25

        self.pistol_mag_size = 8
        self.pistol_ammo = 8  # Bullets currently in the gun
        self.pistol_reserve = 24  # Bullets in your pocket
        self.is_reloading = False
        self.reload_timer = 0
        self.reload_duration = 1500

        self.adrenaline_timer = 0
        self.is_attacking = False
        self.is_aiming = False  # NEW: Track aiming state
        self.pistol_range = 250

        self.anims = {
            "idle": [load_anim(f"Game_project/assets/sprites/MC_anim/MC_idle{i}.png", self.size) for i in range(1, 3)],
            "idle_pistol": [load_anim(f"Game_project/assets/sprites/MC_anim/MC_pistol_idle{i}.png", self.size) for i in range(1, 3)],
            "idle_melee": [load_anim(f"Game_project/assets/sprites/MC_anim/MC_melee_idle{i}.png", self.size) for i in range(1, 3)],
            "walk": [load_anim(f"Game_project/assets/sprites/MC_anim/MC_walk{i}.png", self.size) for i in range(1, 5)],
            "run": [load_anim(f"Game_project/assets/sprites/MC_anim/MC_run{i}.png", self.size) for i in range(1, 5)],
            "walk_gun": [load_anim(f"Game_project/assets/sprites/MC_anim/MC_walk_hold_gun{i}.png", self.size) for i in range(1, 5)],
            "walk_knife": [load_anim(f"Game_project/assets/sprites/MC_anim/MC_walk_hold_knife{i}.png", self.size) for i in range(1, 5)],
            "pistol_shot": [load_anim(f"Game_project/assets/sprites/MC_anim/MC_pistol{i}.png", self.size) for i in range(1, 3)],
            "pistol_shot_crouch": [load_anim(f"Game_project/assets/sprites/MC_anim/MC_pistol_crouch{i}.png", self.size) for i in range(1, 3)],
            "melee": [load_anim(f"Game_project/assets/sprites/MC_anim/MC_melee_attack{i}.png", self.size) for i in range(1, 3)],
            "melee_crouch": [load_anim(f"Game_project/assets/sprites/MC_anim/MC_melee_attack_crouch{i}.png", self.size) for i in range(1, 3)],
            "crouch": [load_anim("Game_project/assets/sprites/MC_anim/MC_crouch.png", self.size)]
        }

        self.state = "idle"
        self.frame_index = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_duration = 400

        self.image = self.anims[self.state][0]
        self.rect = self.image.get_rect(center=(100, GAME_HEIGHT - 100))
        self.pos_x = float(self.rect.x)
        self.pos_y = float(self.rect.y)
        self.facing_right = True

        self.invincible = False
        self.invincibility_timer = 0
        self.i_frame_duration = 500



        self.vel_y = 0
        self.stamina = 100
        self.hp = 100
        self.max_hp = 100
        self.max_stamina = 100
        self.max_sanity = 100
        self.is_fatigued = False
        self.inventory = Inventory()
        self.sanity = 100
        self.debug_ray = (0, 0, 0, 0)

    def update(self, platforms, enemies):
        self.handle_movement()
        self.check_wall_collision()
        self.apply_gravity()
        self.check_collisions(platforms)
        self.animate()

        if self.is_reloading:
            now = pygame.time.get_ticks()
            if now - self.reload_timer >= self.reload_duration:
                self.complete_reload()

        if self.invincible:
            if pygame.time.get_ticks() - self.invincibility_timer > self.i_frame_duration:
                self.invincible = False

        if self.is_attacking:
            now = pygame.time.get_ticks()

            # 1. Trigger damage at frame 1 for BOTH Pistol and Knife
            if int(self.frame_index) == 1 and not hasattr(self, 'shot_fired'):
                # Check for Pistol OR Knife/Melee states
                if "pistol_shot" in self.state or "melee" in self.state:
                    self.perform_attack(enemies)
                self.shot_fired = True

            # 2. End Attack Logic (No changes needed here, just ensure timings match)
            custom_timings = {
                "pistol_shot": [100, 600],
                "pistol_shot_crouch": [100, 600],
                "melee": [150, 400],
                "melee_crouch": [150, 400]
            }

            if self.state in custom_timings:
                if int(self.frame_index) == 1:
                    last_frame_duration = custom_timings[self.state][1]
                    if now - self.last_update >= last_frame_duration:
                        self.is_attacking = False
                        if hasattr(self, 'shot_fired'): del self.shot_fired




    def start_reload(self):
        # Only reload if: not already reloading, mag isn't full, and we have bullets in reserve
        if not self.is_reloading and self.pistol_ammo < self.pistol_mag_size and self.pistol_reserve > 0:
            self.is_reloading = True
            self.reload_timer = pygame.time.get_ticks()
            print("Reload started...")

    def complete_reload(self):
        # Calculate how many bullets we need to fill the mag
        needed = self.pistol_mag_size - self.pistol_ammo

        # Take either what we need, or whatever is left in reserve (if less than needed)
        transfer = min(needed, self.pistol_reserve)

        self.pistol_ammo += transfer
        self.pistol_reserve -= transfer
        self.is_reloading = False
        print("Reload complete!")

    def perform_attack(self, enemies):
        item = self.inventory.get_active_item()
        attack_range = self.pistol_range if item == "Pistol" else 10

        # 1. DEFINE OFFSETS (Keeping your existing logic)
        if item == "Pistol":
            off_x = (25 if self.facing_right else -25) if "crouch" in self.state else (30 if self.facing_right else -30)
            off_y = -12 if "crouch" in self.state else -15
        else:  # Melee
            off_x = 5 if self.facing_right else -5
            off_y = -10 if "crouch" in self.state else -5

        # 2. CALCULATE POSITIONS
        start_x = self.rect.centerx + off_x
        start_y = self.rect.centery + off_y
        direction = 1 if self.facing_right else -1
        end_x = start_x + (attack_range * direction)

        # 3. CREATE HITBOX
        hit_height = 4 if item == "Pistol" else 60
        hit_box = pygame.Rect(min(start_x, end_x), start_y - (hit_height // 2), abs(start_x - end_x), hit_height)

        # 4. DAMAGE LOGIC (Single Target for Pistol)
        hit_enemies = []
        for enemy in enemies:
            if hit_box.colliderect(enemy.rect):
                hit_enemies.append(enemy)

        if hit_enemies:
            if item == "Pistol":
                if self.facing_right:
                    target = min(hit_enemies, key=lambda e: e.rect.x)
                else:
                    target = max(hit_enemies, key=lambda e: e.rect.right)

                # --- BOSS CHECK ---
                if isinstance(target, Boss):
                    if target.state == "STUNNED":
                        target.hp -= 25
                        print(f"Boss Hit! HP: {target.hp}")
                    else:
                        print("Deflected! Boss is flying.")
                else:
                    target.take_damage(25)

                end_x = target.rect.centerx
            else:
                # Melee logic
                for enemy in hit_enemies:
                    if isinstance(enemy, Boss):
                        if enemy.state == "STUNNED": enemy.hp -= 45
                    else:
                        enemy.take_damage(45)

        # 5. DEBUG RAY
        self.debug_ray = (start_x, start_y, end_x, start_y)
    def handle_movement(self):
        # 1. Check Mouse Buttons for Aiming
        mouse_buttons = pygame.mouse.get_pressed()
        # Right click to aim (Button index 2 is RMB)
        self.is_aiming = mouse_buttons[2]

        if self.is_attacking:
            return

        keys = pygame.key.get_pressed()
        old_state = self.state

        # --- FIX: Define these at the start so they always exist ---
        moving = False
        is_running = False
        can_run = False
        vx = 0

        if keys[pygame.K_a]: self.facing_right = False
        if keys[pygame.K_d]: self.facing_right = True

        if self.stamina <= 0: self.is_fatigued = True
        if self.is_fatigued and self.stamina >= self.max_stamina: self.is_fatigued = False

        is_crouching = keys[pygame.K_LCTRL]

        # 2. MOVEMENT
        if not is_crouching and not self.is_aiming:
            current_speed = PLAYER_SPEED
            can_run = keys[pygame.K_LSHIFT] and not self.is_fatigued and self.stamina > 0

            if (keys[pygame.K_a] or keys[pygame.K_d]):
                moving = True

            if can_run and moving:
                current_speed *= 2.0
                is_running = True
                self.frame_duration = 180

                # --- Adrenaline Logic integrated here ---
                if self.adrenaline_timer > 0:
                    self.adrenaline_timer -= 1
                else:
                    self.stamina -= 0.6
            else:
                self.frame_duration = 400
                recovery = 0.15 if moving else 0.3
                self.stamina = min(self.max_stamina, self.stamina + recovery)

            if keys[pygame.K_a]: vx -= current_speed
            if keys[pygame.K_d]: vx += current_speed
            self.pos_x += vx
        else:
            # Recovery when aiming/crouching
            self.stamina = min(self.max_stamina, self.stamina + 0.3)
            if self.adrenaline_timer > 0: self.adrenaline_timer -= 1

        # Apply limits
        if self.pos_x < 0: self.pos_x = 0
        if self.pos_x > GAME_WIDTH - self.rect.width: self.pos_x = GAME_WIDTH - self.rect.width
        self.rect.x = int(self.pos_x)
            # Sync the rect to the forced position
        self.rect.x = int(self.pos_x)

        # 3. STATE DETERMINATION
        item = self.inventory.get_active_item()

        # Check for Aiming FIRST (even if crouching)
        if self.is_aiming and item == "Pistol":
            self.state = "pistol_shot_crouch" if is_crouching else "pistol_shot"
        elif is_crouching:
            self.state = "crouch"
        elif moving:
            if is_running:
                self.state = "run"
            elif item == "Pistol":
                self.state = "walk_gun"
            elif item == "Knife":
                self.state = "walk_knife"
            else:
                self.state = "walk"
        else:
            if item == "Pistol":
                self.state = "idle_pistol"
            elif item == "Knife":
                self.state = "idle_melee"
            else:
                self.state = "idle"

        if self.state != old_state:
            self.frame_index = 0
            self.last_update = pygame.time.get_ticks()

    def apply_gravity(self):
        self.vel_y += GRAVITY
        self.pos_y += self.vel_y
        # Sync the rect bottom to our float tracker
        self.rect.bottom = int(self.pos_y + self.size[1])

    def check_wall_collision(self):
        # Hard limit for the elevator back wall
        # If the player tries to go further left than the elevator wall, stop them
        if self.pos_x < 5:  # Adjust this number to match your elevator back
            self.pos_x = 5
            self.rect.x = int(self.pos_x)

    def check_collisions(self, platforms):
        self.on_ground = False
        for plat in platforms:
            if self.rect.colliderect(plat.rect):
                if self.vel_y > 0:
                    # Snap feet to platform top
                    self.rect.bottom = plat.rect.top + self.y_offset
                    # Update our tracker so it knows where the feet are
                    self.pos_y = float(self.rect.bottom - self.size[1])
                    self.vel_y = 0
                    self.on_ground = True

    def animate(self):
        frames = self.anims.get(self.state, self.anims["idle"])
        now = pygame.time.get_ticks()

        custom_timings = {
            "pistol_shot": [100, 800],
            "pistol_shot_crouch": [100, 800],
            "melee": [150, 600],
            "melee_crouch": [150, 600]
        }



        # Get duration for current frame
        if self.state in custom_timings:
            current_duration = custom_timings[self.state][int(self.frame_index)]
        else:
            current_duration = self.frame_duration

        is_pistol_state = "pistol_shot" in self.state

        if is_pistol_state and self.is_aiming and not self.is_attacking:
            # Aiming stance: freeze on frame 0
            self.frame_index = 0
        else:
            if now - self.last_update > current_duration:
                # If we are attacking, don't loop back to 0 automatically.
                # Stay on the last frame (index 1). The 'update' method will reset it.
                if self.is_attacking and int(self.frame_index) >= len(frames) - 1:
                    pass  # Keep frame_index at 1
                else:
                    self.frame_index = (self.frame_index + 1) % len(frames)
                    self.last_update = now

        # Rendering
        img = frames[int(self.frame_index)]
        self.image = pygame.transform.flip(img, not self.facing_right, False)
        self.rect.x, self.rect.y = int(self.pos_x), int(self.pos_y)

        # 1. Update the Image
        img = frames[int(self.frame_index)]
        self.image = pygame.transform.flip(img, not self.facing_right, False)

        # 2. Re-create the Hitbox (self.rect)
        # We start with the full size, then shrink it
        self.rect = self.image.get_rect()

        if "crouch" in self.state:
            # -20 width, -28 height (Ducking)
            self.rect = self.rect.inflate(-25, -17)
        else:
            # -20 width, full height (Standing)
            self.rect = self.rect.inflate(-25, 0)

        # 3. Anchor the Hitbox to the Bottom
        # This ensures that even when the box gets shorter, the bottom
        # stays at (pos_y + 64), which is where the feet are.
        current_x_offset = 10 if self.facing_right else -10

        self.rect.centerx = int(self.pos_x - current_x_offset + self.size[0] // 2)
        self.rect.bottom = int(self.pos_y + self.size[1])

        if self.invincible:
            # Simple flicker effect: only show the image every other frame
            if (pygame.time.get_ticks() // 50) % 2 == 0:
                self.image.set_alpha(100)  # Make semi-transparent
            else:
                self.image.set_alpha(255)
        else:
            self.image.set_alpha(255)

    def _trigger_attack(self):
        item = self.inventory.get_active_item()
        keys = pygame.key.get_pressed()
        is_crouching = keys[pygame.K_LCTRL]

        # Block attack if currently reloading
        if self.is_reloading:
            return

        if not self.is_attacking:
            if item == "Pistol" and self.is_aiming:
                # Check for ammo before shooting
                if self.pistol_ammo > 0:
                    self.is_attacking = True
                    self.pistol_ammo -= 1  # Reduce ammo in mag
                    self.state = "pistol_shot_crouch" if is_crouching else "pistol_shot"
                    self.frame_index = 0
                    self.last_update = pygame.time.get_ticks()
                else:
                    print("Out of ammo! Press R to reload.")  # Optional: add a 'click' sound effect here

            elif item == "Knife":
                self.is_attacking = True
                self.state = "melee_crouch" if is_crouching else "melee"
                self.frame_index = 0
                self.last_update = pygame.time.get_ticks()

    def handle_input(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                # --- R: RELOAD ---
                if event.key == pygame.K_r:
                    self.start_reload()

                # --- Q: CYCLE NEXT SLOT ---
                if event.key == pygame.K_q:
                    self.inventory.next_slot()

                # --- 1 to 6: DIRECT SELECTION ---
                if pygame.K_1 <= event.key <= pygame.K_6:
                    index = event.key - pygame.K_1
                    if index < len(self.inventory.slots):
                        self.inventory.select_slot(index)

                # --- E: USE ITEM ---
                if event.key == pygame.K_e:
                    self.inventory.use_active_item(self)

            # Left Click to Attack
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self._trigger_attack()

    def take_damage(self, amount):
        now = pygame.time.get_ticks()

        if not self.invincible:
            self.hp -= amount
            self.invincible = True
            self.invincibility_timer = now
            print(f"Player hit! HP remaining: {self.hp}")

            if self.hp <= 0:
                self.hp = 0
                self.die()

    def die(self):
        # You can expand this later with a game over screen
        print("Game Over!")
        # For now, let's just reset HP as a placeholder
        # self.hp = self.max_hp