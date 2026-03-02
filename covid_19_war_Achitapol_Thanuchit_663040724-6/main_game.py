import random
import pygame
import math
import json
import os

#=============================================================================
#1. SETUP & CONFIGURATION
#=============================================================================
pygame.init()
pygame.mixer.init(44100, -16, 2, 512)

WIDTH = 600
HEIGHT = 800
FPS = 60
STATS_FILE = "stats.json"

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Covid-19 War - Achitapol Thanuchit Version")

#Assets
bg_gameplay = pygame.image.load("Assets/images/city.png").convert()
bg_gameplay = pygame.transform.smoothscale(bg_gameplay, (WIDTH, HEIGHT))

#Player animation
PLAYER_SIZE = (128, 72)

def load_and_scale(path, size):
    image = pygame.image.load(path).convert_alpha()
    return pygame.transform.scale(image, size)

#Create global lists for animations
IDLE_ANIMS = [load_and_scale("Assets/images/Thailand_ball_idle.png", PLAYER_SIZE)]
ATTACK_ANIMS = [load_and_scale(f"Assets/images/Thailand_ball_attack{i}.png", PLAYER_SIZE) for i in range(1, 4)]
LEFT_ANIMS = [load_and_scale(f"Assets/images/Thailand_ball_right{i}.png", PLAYER_SIZE) for i in range(1, 3)]
RIGHT_ANIMS = [load_and_scale(f"Assets/images/Thailand_ball_left{i}.png", PLAYER_SIZE) for i in range(1, 3)]

#Icons
ICON_SIZE = (50, 50)
icon_heal = pygame.transform.scale(pygame.image.load("Assets/images/heal.png").convert_alpha(), ICON_SIZE)
icon_double = pygame.transform.scale(pygame.image.load("Assets/images/double_atk.png").convert_alpha(), ICON_SIZE)
icon_fire = pygame.transform.scale(pygame.image.load("Assets/images/speed_attack.png").convert_alpha(), ICON_SIZE)
icon_shield = pygame.transform.scale(pygame.image.load("Assets/images/shield.png").convert_alpha(), ICON_SIZE)

BOSS_SIZE = (150, 150)

BOSS_IMG_ORIG = pygame.transform.scale(
    pygame.image.load("Assets/images/boss.png").convert_alpha(), BOSS_SIZE)

#Load Boss Bullet Asset 
boss_bullet_raw = pygame.image.load("Assets/images/boss_bullet_2t.png").convert_alpha()

#Load and Pre-Scale Player Bullet 
raw_bullet = pygame.image.load('Assets/images/cure.png').convert_alpha()

reduce_factor = 0.25
new_w = int(raw_bullet.get_width() * reduce_factor)
new_h = int(raw_bullet.get_height() * reduce_factor)

player_bullet_scaled = pygame.transform.smoothscale(raw_bullet, (new_w, new_h))

#Load and Pre-Scale Player ult
increase_factor = 1.25
new_w = int(raw_bullet.get_width() * increase_factor)
new_h = int(raw_bullet.get_height() * increase_factor)

player_bullet_scaled_ult = pygame.transform.smoothscale(raw_bullet, (new_w, new_h))

#Load and Pre-Scale Boss bullet
SCALE_FACTOR = 0.25

#Calculate the new dimensions based on your original 86x115 size
new_width = int(boss_bullet_raw.get_width() * SCALE_FACTOR)
new_height = int(boss_bullet_raw.get_height() * SCALE_FACTOR)

#Scale it once and save it to a global variable
boss_bullet_img = pygame.transform.smoothscale(boss_bullet_raw, (new_width, new_height))

#Menu assets
menu_bg_frames = [
    pygame.image.load("Assets/images/Bg_menu1.png").convert(),
    pygame.image.load("Assets/images/Bg_menu2.png").convert()
]

#Variables for animation timing
bg_current_frame = 0
bg_last_update = pygame.time.get_ticks()
bg_animation_speed = 500

#Load Title Logo 
logo_img = pygame.image.load("Assets/images/game_title.png").convert_alpha()

#Adjust 400x150 to match the dimensions of your actual logo drawing
LOGO_SIZE = (488, 320)
logo_img = pygame.transform.smoothscale(logo_img, LOGO_SIZE)

BTN_SIZE = (200, 50)

btn_play = pygame.image.load("Assets/images/play_button.png").convert_alpha()
btn_play = pygame.transform.smoothscale(btn_play, BTN_SIZE)

btn_statistic = pygame.image.load("Assets/images/statistic_button.png").convert_alpha()
btn_statistic = pygame.transform.smoothscale(btn_statistic, BTN_SIZE)

btn_guide = pygame.image.load("Assets/images/guide_button.png").convert_alpha()
btn_guide = pygame.transform.smoothscale(btn_guide, BTN_SIZE)

btn_exit = pygame.image.load("Assets/images/exit.png").convert_alpha()
btn_exit = pygame.transform.smoothscale(btn_exit, BTN_SIZE)

btn_back = pygame.image.load("Assets/images/back.png").convert_alpha()
btn_back = pygame.transform.smoothscale(btn_back, BTN_SIZE)

btn_resume = pygame.image.load("Assets/images/resume.png").convert_alpha()
btn_resume = pygame.transform.smoothscale(btn_resume, BTN_SIZE)

btn_return_to_menu = pygame.image.load("Assets/images/return_to_menu.png").convert_alpha()
btn_return_to_menu = pygame.transform.smoothscale(btn_return_to_menu, BTN_SIZE)

btn_restart = pygame.image.load("Assets/images/restart.png").convert_alpha()
btn_restart = pygame.transform.smoothscale(btn_restart, BTN_SIZE)

#HOVER SETTINGS
HOVER_WIDTH = 180
HOVER_HEIGHT = 50
HOVER_RADIUS = 15

#If you want it very subtle, use 50. If you want it distinct, use 200.
HOVER_ALPHA = 128

#Create a temporary surface that handles transparency
HOVER_SURF = pygame.Surface((HOVER_WIDTH, HOVER_HEIGHT), pygame.SRCALPHA)

#Draw the shape onto this surface.
#(255, 255, 255) is WHITE. Using white usually looks better for "highlighting".
pygame.draw.rect(
    HOVER_SURF,
    (0, 0, 0, HOVER_ALPHA), #White with Alpha
    (0, 0, HOVER_WIDTH, HOVER_HEIGHT),
    border_radius=HOVER_RADIUS
)

bg_y1 = 0
bg_y2 = -HEIGHT
scroll_speed = 1

ult_ready_sound_played = False
current_track = "none"
boss_warning_active = False
boss_warning_start = 0
clock = pygame.time.Clock()
last_hovered_action = None


#ENEMY CONFIGURATION 
ENEMY_TYPES = {
    "basic": {
        "image": "Assets/images/covid-19_basic.png",
        "hp": 3, "speed_min": 4, "speed_max": 6, "damage": 10, "score": 100, "ult_gain": 3, "scale": (50, 50)
    },
    "tank": {
        "image": "Assets/images/covid-19_tank.png",
        "hp": 7, "speed_min": 3, "speed_max": 4, "damage": 20, "score": 300, "ult_gain": 6, "scale": (80, 80)
    },
    "fast": {
        "image": "Assets/images/covid-19_speed.png",
        "hp": 1, "speed_min": 8, "speed_max": 12, "damage": 5, "score": 200, "ult_gain": 1, "scale": (50, 50)
    }
}

for name, data in ENEMY_TYPES.items():
    img = pygame.image.load(data["image"]).convert_alpha()
    data["ready_image"] = pygame.transform.scale(img, data["scale"])

#Stat manager for save player data
class StatsManager:
    def __init__(self):
        self.data = {
            "kill_count": 0,
            "top_score": 0,
            "die_count": 0,
            "max_boss_lvl": 0
        }
        self.load()

    def load(self):
        if os.path.exists(STATS_FILE):
            with open(STATS_FILE, "r") as f:
                self.data = json.load(f)

    def save(self):
        with open(STATS_FILE, "w") as f:
            json.dump(self.data, f)

    def update_stat(self, key, value, cumulative=True):
        if cumulative:
            self.data[key] += value
        else:  #For Top Score or Max Level
            if value > self.data[key]:
                self.data[key] = value
        self.save()

#Sound & Music
player_hurt_sound = pygame.mixer.Sound("Assets/sound/dogwolf123-retro-hurt-sound-03-474780.mp3")
player_hurt_sound.set_volume(0.5)

boom_sound = pygame.mixer.Sound("Assets/sound/boom.wav")
boom_sound.set_volume(0.4)

sword_sound = pygame.mixer.Sound('Assets/sound/dogwolf123-retro-zap-sound-06-474813.mp3')
sword_sound.set_volume(0.2)

button_hover = pygame.mixer.Sound('Assets/sound/freesound_community-one_beep-99630.mp3')
button_hover.set_volume(1)

button_click = pygame.mixer.Sound('Assets/sound/floraphonic-90s-game-ui-5-185098.mp3')
button_click.set_volume(1)

receive_item = pygame.mixer.Sound('Assets/sound/lesiakower-coin-collect-retro-8-bit-sound-effect-145251.mp3')
receive_item.set_volume(0.4)

ultimate_sound = pygame.mixer.Sound('Assets/sound/daviddumaisaudio-abstract-magic-whoosh-03-204485_edited.mp3')
ultimate_sound.set_volume(1)

boss_theme = pygame.mixer.Sound('Assets/sound/Retro-Boss-Uprising.ogg')
boss_theme.set_volume(0.7)

ultimate_full_sound = pygame.mixer.Sound('Assets/sound/dogwolf123-retro-power-up-sound-03-474809.mp3')
ultimate_full_sound.set_volume(1)

heal_sound = pygame.mixer.Sound('Assets/sound/lolo_s-power-up-474087.mp3')
heal_sound.set_volume(0.8)

shield_buff_sound = pygame.mixer.Sound('Assets/sound/yodguard-warp-magic-1-382386.mp3')
shield_buff_sound.set_volume(1)

double_attack_sound = pygame.mixer.Sound('Assets/sound/dogwolf123-retro-power-up-sound-02-474798.mp3')
double_attack_sound.set_volume(1)

speed_up_attack_sound = pygame.mixer.Sound('Assets/sound/freesound_community-power_up_grab-88510.mp3')
speed_up_attack_sound.set_volume(1)

game_over = pygame.mixer.Sound('Assets/sound/freesound_community-game-over-arcade-6435.mp3')
game_over.set_volume(2)

stats_manager = StatsManager()

#=============================================================================
#2. CLASSES & Helper
#=============================================================================

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        #Simply reference the global lists we loaded outside
        self.anim_idle = IDLE_ANIMS
        self.anim_left = LEFT_ANIMS
        self.anim_right = RIGHT_ANIMS
        self.anim_attack = ATTACK_ANIMS

        self.frame_index = 0
        self.current_anim_list = self.anim_idle
        self.image = self.anim_idle[0]
        self.rect = self.image.get_rect()
        self.rect.midbottom = (WIDTH / 2, HEIGHT - 20)

        self.radius = 25
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 100
        self.is_attacking = False
        self.attack_timer = 0

        #Stats
        self.life = 100
        self.ult_charge = 0
        self.score = 0
        self.bonus_score = 0
        self.speedx = 0
        self.move_speed = 6
        self.shoot_delay = 200
        self.last_shot = pygame.time.get_ticks()

        #Buff Timers
        self.has_shield = False

        self.double_attack = False
        self.double_attack_end = 0
        self.double_attack_duration = 10000

        self.rapid_fire = False
        self.rapid_fire_end = 0
        self.rapid_fire_duration = 10000

        self.last_hit_time = 0
        self.original_image = self.image.copy()

    def update(self):
        #1. Movement
        self.speedx = 0
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]: self.speedx = -self.move_speed
        if keys[pygame.K_RIGHT]: self.speedx = self.move_speed

        self.rect.x += self.speedx
        if self.rect.left < 0: self.rect.left = 0
        if self.rect.right > WIDTH: self.rect.right = WIDTH

        #2. Check Buff Timers
        now = pygame.time.get_ticks()
        if self.double_attack and now > self.double_attack_end:
            self.double_attack = False

        if self.rapid_fire and now > self.rapid_fire_end:
            self.rapid_fire = False
            self.shoot_delay = 250  #Reset to normal

        #3. Animation
        old_list = self.current_anim_list
        if self.is_attacking and now - self.attack_timer > 300:
            self.is_attacking = False

        if self.is_attacking:
            self.current_anim_list = self.anim_attack
            self.frame_rate = 80
        elif self.speedx < 0:
            self.current_anim_list = self.anim_left
            self.frame_rate = 100
        elif self.speedx > 0:
            self.current_anim_list = self.anim_right
            self.frame_rate = 100
        else:
            self.current_anim_list = self.anim_idle
            self.frame_rate = 200

        if old_list != self.current_anim_list:
            self.frame_index = 0

        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame_index += 1
            if self.frame_index >= len(self.current_anim_list):
                self.frame_index = 0
            self.original_image = self.current_anim_list[self.frame_index]
            self.image = self.original_image.copy()

        #Red flash
        if pygame.time.get_ticks() - self.last_hit_time < 200:
            tint = pygame.Surface(self.image.get_size()).convert_alpha()
            tint.fill((255, 0, 0, 100))
            self.image = self.original_image.copy()
            self.image.blit(tint, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        else:
            self.image = self.original_image.copy()

    def shoot(self):
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            self.is_attacking = True
            self.attack_timer = now
            sword_sound.play()
            if self.double_attack:

                #Bullet 1: Spawns 50 pixels higher (ahead)
                c1 = Cure(self.rect.centerx, self.rect.top - 50)

                #Bullet 2: Spawns at normal position (behind)
                c2 = Cure(self.rect.centerx, self.rect.top)

                allsprites.add(c1, c2)
                cures.add(c1, c2)
            else:
                cure = Cure(self.rect.centerx, self.rect.top)
                allsprites.add(cure)
                cures.add(cure)

    def cast_ultimate(self):
        if self.ult_charge >= 100:
            self.ult_charge = 0
            ultimate_sound.play()

            #Spawn a single persistent slash
            slash = UltSlash(self.rect.centerx, self.rect.top)
            allsprites.add(slash)
            ult_slash.add(slash)

    def take_damage(self, amount):
        if self.has_shield:
            self.has_shield = False
            return
        self.life -= amount
        self.last_hit_time = pygame.time.get_ticks()
        player_hurt_sound.play()

    def add_ult(self, amount):
        self.ult_charge += amount
        if self.ult_charge > 100: self.ult_charge = 100

    def activate_double_attack(self):
        self.double_attack = True
        self.double_attack_end = pygame.time.get_ticks() + self.double_attack_duration

    def activate_rapid_fire(self):
        self.rapid_fire = True
        self.shoot_delay = 100
        self.rapid_fire_end = pygame.time.get_ticks() + self.rapid_fire_duration

    def reset_buffs(self):
        self.move_speed = 6
        self.shoot_delay = 250
        self.has_shield = False
        self.double_attack = False
        self.rapid_fire = False
        self.ult_charge = 0

class Boss(pygame.sprite.Sprite):
    def __init__(self, spawn_count):
        super().__init__()
        self.current_pattern = random.randint(0, 4)
        self.pattern_timer = pygame.time.get_ticks()
        self.ult_can_hit = True
        self.ult_hit_time = 0
        self.ult_cooldown = 1000
        self.bullet_density = max(10, 30 - (spawn_count * 2))

        self.image_orig = BOSS_IMG_ORIG
        self.image = self.image_orig.copy()

        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH / 2
        self.rect.y = -200

        #Difficulty Scaling
        multiplier = pow(1.5, spawn_count)
        self.hp = 30 * multiplier
        self.max_hp = self.hp
        self.level_display = spawn_count + 1

        self.entered = False
        self.last_shot = pygame.time.get_ticks()
        self.shoot_delay = 500
        self.angle = 0
        self.last_hit_time = 0
        self.hit_cooldown = 150

    def update(self):
        now = pygame.time.get_ticks()

        #--- 1. ULTIMATE COOLDOWN RESET (The fix for your bug!) ---
        if not self.ult_can_hit:
            if now - self.ult_hit_time > self.ult_cooldown:
                self.ult_can_hit = True

        #--- 2. ENTRANCE & MOVEMENT LOGIC ---
        if self.rect.y < 120:
            self.rect.y += 2
            #Set the starting point for the x position while entering
            #so it doesn't "snap" when it finishes
            self.rect.centerx = WIDTH // 2
            self.entry_finished_time = now  #Keep updating this until we are in place
        else:
            self.entered = True
            #Calculate time passed SINCE the boss reached y=50
            #This makes the sine wave start at 0, which is the center
            time_in_position = now - self.entry_finished_time

            #Smoothly start the sine wave movement
            self.rect.x = (WIDTH // 2 - self.rect.width // 2) + math.sin(time_in_position / 1000) * 150

        #--- 3. SHOOTING & PATTERN LOGIC ---
        if self.entered:
            #Change pattern every 3 seconds
            if now - self.pattern_timer > 3000:
                new_pattern = random.randint(0, 4)
                #Ensure it doesn't pick the same pattern twice in a row
                while new_pattern == self.current_pattern:
                    new_pattern = random.randint(0, 4)
                self.current_pattern = new_pattern
                self.pattern_timer = now

            #Fire the current pattern
            if now - self.last_shot > self.shoot_delay:
                self.last_shot = now
                self.shoot_pattern(now, self.current_pattern)

        if now - self.last_hit_time < 100:
            self.image = self.image_orig.copy()
            self.image.set_alpha(150)

        elif not self.ult_can_hit:
            #When immune to Ult, make him slightly transparent
            self.image = self.image_orig.copy()
            self.image.set_alpha(150)

        else:
            #Normal state
            self.image = self.image_orig
            self.image.set_alpha(255)

    def shoot_pattern(self, now, pattern):
        base_speed = 4 + (self.level_display * 0.25)

        if pattern == 0:
            #DOWNWARD FAN (Fast)
            for i in range(60, 121, self.bullet_density):
                self.spawn_bullet(self.rect.centerx, self.rect.centery, i, base_speed + 1)

        elif pattern == 1:
            #SPIRAL (Medium)
            self.angle += 20
            self.spawn_bullet(self.rect.centerx, self.rect.centery, self.angle, base_speed)
            self.spawn_bullet(self.rect.centerx, self.rect.centery, self.angle + 180, base_speed)

        elif pattern == 2:
            #RANDOM SPRAY (Variable Speeds)
            for _ in range(3):
                angle = random.randrange(60, 120)
                self.spawn_bullet(self.rect.centerx, self.rect.bottom, angle, random.uniform(3, base_speed + 2))

        elif pattern == 3:
            #THE FULL CIRCLE (Slower, but dense)
            for i in range(0, 360, self.bullet_density):
                self.spawn_bullet(self.rect.centerx, self.rect.centery, i, base_speed - 1)

        elif pattern == 4:
            #TARGETED BURST (Sniping the player)
            dx = player.rect.centerx - self.rect.centerx
            dy = player.rect.centery - self.rect.centery
            target_angle = math.degrees(math.atan2(dy, dx))

            for offset in [-10, -5, 0, 5, 10]:
                self.spawn_bullet(self.rect.centerx, self.rect.centery, target_angle + offset, base_speed + 1)

    def spawn_bullet(self, x, y, angle_deg, speed):
        angle_rad = math.radians(angle_deg)
        #Uses your pre-scaled BossBullet asset inside that class
        boss_bullet = BossBullet(x, y, speed * math.cos(angle_rad), speed * math.sin(angle_rad))
        allsprites.add(boss_bullet)
        boss_bullets.add(boss_bullet)

    def take_hit_from_ult(self, damage):
        #1. Check the Boolean Flag
        if self.ult_can_hit:
            self.hp -= damage
            self.last_hit_time = pygame.time.get_ticks()
            self.ult_can_hit = False
            self.ult_hit_time = pygame.time.get_ticks()  #Start the timer
            #Debug
            #print(f"HIT! Boss HP is now: {self.hp}")

            if self.hp <= 0:
                self.hp = 0
                return True  #Boss Died
            else:
                pass

        return False  #Boss survived OR was immune

class BossBullet(pygame.sprite.Sprite):
    def __init__(self, x, y, speed_x, speed_y):
        super().__init__()
        #Use the pre-scaled image from your assets
        self.image = boss_bullet_img

        #Get the rect to handle positioning and collisions
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.speedx = speed_x
        self.speedy = speed_y

    def update(self):
        self.rect.x += self.speedx
        self.rect.y += self.speedy

        #Delete the bullet if it goes off-screen
        if (self.rect.top > HEIGHT or self.rect.bottom < 0 or
                self.rect.left > WIDTH or self.rect.right < 0):
            self.kill()

class Enemy(pygame.sprite.Sprite):
    def __init__(self, e_type):
        super().__init__()
        stats = ENEMY_TYPES[e_type]

        self.image_orig = stats["ready_image"]
        self.image = self.image_orig.copy()

        self.rect = self.image.get_rect()
        self.hp = stats["hp"]
        self.damage = stats["damage"]
        self.score_val = stats["score"]
        self.ult_val = stats["ult_gain"]

        self.rect.x = random.randrange(0, WIDTH - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        self.speedy = random.randrange(stats["speed_min"], stats["speed_max"])
        self.last_hit_time = 0

    def update(self):
        self.rect.y += self.speedy
        if self.rect.top > HEIGHT:
            self.kill()

        #White flash when hit
        now = pygame.time.get_ticks()
        if now - self.last_hit_time < 150:
            #We still need to copy and blit for the hit effect,
            #but we are doing it from RAM now, not Disk!
            self.image = self.image_orig.copy()
            tint = pygame.Surface(self.image.get_size()).convert_alpha()
            tint.fill((255, 255, 255, 100))
            self.image.blit(tint, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        else:
            #Important: only reset the image if it was actually changed
            #This saves a tiny bit of CPU every frame
            if self.image != self.image_orig:
                self.image = self.image_orig

    def take_hit(self, damage=1):
        self.hp -= damage
        self.last_hit_time = pygame.time.get_ticks()
        if self.hp <= 0:
            self.kill()
            return True
        return False

class Cure(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        #Simply use the pre-scaled image
        self.image = player_bullet_scaled

        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.speedy = -10

    def update(self):
        self.rect.y += self.speedy
        #Kill the bullet if it leaves the top of the screen
        if self.rect.bottom < 0:
            self.kill()

class UltSlash(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()

        self.image = player_bullet_scaled_ult

        self.rect = self.image.get_rect()

        #Center it on the player horizontally
        self.rect.centerx = x
        self.rect.bottom = y  #starts at player position

        self.speedy = -15  #moves upward fast
        self.damage = 25

        #Lifetime control: auto-destroy after traveling full screen
        self.spawn_y = y

    def update(self):
        self.rect.y += self.speedy

        #Kill when it exits the top of screen
        if self.rect.bottom < 0:
            self.kill()

class Item(pygame.sprite.Sprite):
    def __init__(self, item_type):
        super().__init__()
        self.type = item_type

        if self.type == 'heal':
            self.image = icon_heal
        elif self.type == 'double_atk':
            self.image = icon_double
        elif self.type == 'firerate':
            self.image = icon_fire
        elif self.type == 'shield':
            self.image = icon_shield

        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(0, WIDTH - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        self.speedy = 3

    def update(self):
        self.rect.y += self.speedy
        if self.rect.top > HEIGHT:
            self.kill()

def spawn_new_enemy():
    rand = random.random()
    if rand < 0.7:
        e = Enemy("basic") #70%
    elif rand < 0.9:
        e = Enemy("fast") #20%
    else:
        e = Enemy("tank") #10%
    allsprites.add(e)
    enemies.add(e)


def draw_boss_hp(screen, boss_obj):
    ratio = boss_obj.hp / boss_obj.max_hp
    now = pygame.time.get_ticks()

    #1. Shake Logic
    offset_x, offset_y = 0, 0
    if now - boss_obj.last_hit_time < 100:
        offset_x = random.randint(-6, 6)
        offset_y = random.randint(-6, 6)

    #2. New Position (Higher up to clear space for the boss)
    bar_x = (WIDTH // 2 - 150) + offset_x
    bar_y = 80 + offset_y  #Moved up slightly from 80
    bar_width = 300
    bar_height = 18

    #3. Draw Text Above Bar
    boss_label = f"SUPER COVID-19 LV. {boss_obj.level_display}"
    draw_text(screen, boss_label, 22, bar_x + 150, bar_y - 20, (255, 255, 255))

    #4. Draw the Bar Layers
    pygame.draw.rect(screen, (50, 0, 0), (bar_x, bar_y, bar_width, bar_height))
    #Red fill
    pygame.draw.rect(screen, (255, 0, 50), (bar_x, bar_y, bar_width * ratio, bar_height))
    #Border
    pygame.draw.rect(screen, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 2)

def draw_boss_warning(screen):
    alpha = abs(math.sin(pygame.time.get_ticks() / 100) * 255)
    warning_surf = pygame.Surface((WIDTH, 100), pygame.SRCALPHA)
    pygame.draw.rect(warning_surf, (255, 0, 0, 100), (0, 0, WIDTH, 100))
    draw_text(warning_surf, "!!! WARNING: ELITE ENEMY IS APPEAR !!!", 40, WIDTH // 2, 50, (255, 255, 255))
    warning_surf.set_alpha(alpha)
    screen.blit(warning_surf, (0, HEIGHT // 2 - 50))

#=============================================================================
#3. MENU & UI FUNCTIONS
#=============================================================================

def draw_button(image, y_pos, action_state):
    global last_hovered_action

    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()

    #1. Position the button
    #(Center it based on the screen width and y_pos)
    button_rect = image.get_rect(center=(WIDTH // 2, y_pos))

    #DRAW STEP 1: The Button Image
    #Draw the button normally first
    screen.blit(image, button_rect)

    #2. Check Hover logic
    if button_rect.collidepoint(mouse):

        #SOUND LOGIC
        if last_hovered_action != action_state:
            button_hover.play()
            last_hovered_action = action_state

        #DRAW STEP 2: The Hover Overlay
        #Draw the semi-transparent surface ON TOP of the button image
        hover_rect = HOVER_SURF.get_rect(center=button_rect.center)
        screen.blit(HOVER_SURF, hover_rect)

        #CLICK LOGIC
        if click[0] == 1:
            receive_item.play()
            pygame.time.delay(300)
            return action_state

    #3. Reset Tracker if mouse left
    elif last_hovered_action == action_state:
        last_hovered_action = None

    return None

def draw_text(surf, text, size, x, y, color=(255, 255, 255), align="center"):
    text_surface = pygame.font.SysFont("robotto", size).render(str(text), True, color)
    rect = text_surface.get_rect()
    if align == "center":
        rect.midtop = (x, y)
    elif align == "right":
        rect.topright = (x, y)
    surf.blit(text_surface, rect)

def draw_title(image, y_pos):

    float_offset = math.sin(pygame.time.get_ticks() * 0.005) * 5

    rect = image.get_rect(center=(WIDTH // 2, y_pos + float_offset))

    screen.blit(image, rect)

def draw_buff_icon(surf, icon, x, y, duration, end_time):
    #Draw Background

    scaled_icon = pygame.transform.scale(icon, (30, 30))
    surf.blit(scaled_icon, (x, y))

    #Draw Cooldown Overlay (Top to Bottom)
    now = pygame.time.get_ticks()
    time_left = max(0, end_time - now)
    ratio = time_left / duration

    #Inverse ratio for draining effect
    height = int(30 * (1 - ratio))

    s = pygame.Surface((30, height))
    s.set_alpha(150)
    s.fill((0, 0, 0))
    surf.blit(s, (x, y))  #Draw overlay from top

    #Border
    pygame.draw.rect(surf, (255, 255, 255), (x, y, 30, 30), 1)

#=============================================================================
#4. GAME STATES & MAIN LOOP
#=============================================================================

#State Constants
STATE_MENU = "MENU"
STATE_PLAY = "PLAY"
STATE_STATS = "STATS"
STATE_GUIDE = "GUIDE"
STATE_GAMEOVER = "GAMEOVER"
STATE_PAUSE = "PAUSE"

current_state = STATE_MENU
stats_saved = False #To prevent saving stats 60 times a second

#Initialize Groups
allsprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
cures = pygame.sprite.Group()
items = pygame.sprite.Group()
boss_bullets = pygame.sprite.Group()
boss_group = pygame.sprite.Group()
ult_slash = pygame.sprite.Group()
ult_boss_hits = pygame.sprite.groupcollide(boss_group, ult_slash, False, False)
last_item_spawn = pygame.time.get_ticks()

def reset_game():
    global bg_y1, bg_y2, boss_active, next_boss_score, boss_spawn_count
    bg_y1 = 0
    bg_y2 = -HEIGHT
    player.life = 100
    player.score = 0
    player.bonus_score = 0
    player.rect.midbottom = (WIDTH / 2, HEIGHT - 50)
    player.reset_buffs()
    allsprites.empty()
    enemies.empty()
    cures.empty()
    boss_group.empty()
    boss_bullets.empty()
    items.empty()
    allsprites.add(player)
    boss_active = False
    boss_spawn_count = 0
    next_boss_score = 10000
    for i in range(8): spawn_new_enemy()


player = Player()
reset_game()

running = True
while running:
    clock.tick(FPS)


    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_ESCAPE:
                if current_state == STATE_PLAY:
                    current_state = STATE_PAUSE
                elif current_state == STATE_PAUSE:
                    current_state = STATE_PLAY

            if current_state == STATE_PLAY:
                if event.key == pygame.K_SPACE: player.shoot()
                if event.key == pygame.K_z: player.cast_ultimate()

            if current_state == STATE_GAMEOVER:
                if event.key == pygame.K_RETURN:  #Press Enter to go home
                    current_state = STATE_MENU

    now = pygame.time.get_ticks()
    if now - bg_last_update > bg_animation_speed:
        bg_current_frame = (bg_current_frame + 1) % len(menu_bg_frames)
        bg_last_update = now
    #State machine
    if current_state == STATE_MENU:
        if current_state == STATE_MENU:
            if current_track != "menu":
                pygame.mixer.music.load('Assets/sound/Pixel-Run.ogg')
                pygame.mixer.music.set_volume(0.5)
                pygame.mixer.music.play(-1)
                current_track = "menu"

        screen.blit(menu_bg_frames[bg_current_frame], (0, 0))

        draw_title(logo_img, 170)

        #Buttons
        if draw_button(btn_play, 350, STATE_PLAY):
            reset_game()
            stats_saved = False
            current_state = STATE_PLAY

            pygame.mixer.music.load('Assets/sound/Retro-Battle-Loop.ogg')
            pygame.mixer.music.set_volume(0.6)
            pygame.mixer.music.play(-1)

        if draw_button(btn_statistic, 420, STATE_STATS):
            current_state = STATE_STATS

        if draw_button(btn_guide, 490, STATE_GUIDE):
            current_state = STATE_GUIDE

        if draw_button(btn_exit, 560, "EXIT") == "EXIT":
            running = False

    if current_state == STATE_STATS:
        #Draw animated background
        screen.blit(menu_bg_frames[bg_current_frame], (0, 0))

        #Optional dimming overlay for stats
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))
        draw_text(screen, "GLOBAL STATISTICS", 45, WIDTH // 2, 100, (255, 215, 0))
        stats_entries = [
            f"Total Kills: {stats_manager.data['kill_count']}",
            f"Top Score: {stats_manager.data['top_score']}",
            f"Total Deaths: {stats_manager.data['die_count']}",
            f"Max Boss Level: {stats_manager.data['max_boss_lvl']}"
        ]

        for i, entry in enumerate(stats_entries):
            draw_text(screen, entry, 35, WIDTH // 2, 250 + (i * 60))  #Increased spacing to 60

        if draw_button(btn_back, 560, STATE_MENU):
            current_state = STATE_MENU

    #PLAY STATE
    elif current_state == STATE_PLAY:
        #for cheating XD
        #player.ult_charge = 100

        #1. INFINITE SCROLL LOGIC
        #Move both background positions downward
        bg_y1 += scroll_speed
        bg_y2 += scroll_speed

        #If a background image moves off the bottom, reset it to the top
        if bg_y1 >= HEIGHT:
            bg_y1 = -HEIGHT
        if bg_y2 >= HEIGHT:
            bg_y2 = -HEIGHT

        #2. DRAWING (Order is vital)
        #Draw the two background pieces
        screen.blit(bg_gameplay, (0, bg_y1))
        screen.blit(bg_gameplay, (0, bg_y2))

        if player.life > 0:
            allsprites.update()

            #Boss logic
            if not boss_active:
                if player.score >= next_boss_score and not boss_warning_active:
                    boss_warning_active = True
                    boss_warning_start = pygame.time.get_ticks()

                    #Stop the background music smoothly
                    pygame.mixer.music.fadeout(500)

                    #Play the boss track from RAM (Instant!)
                    boss_theme.play(loops=-1)
                    current_track = "boss"

                if boss_warning_active:
                    draw_boss_warning(screen)
                    if pygame.time.get_ticks() - boss_warning_start > 2000:
                        boss_warning_active = False
                        boss_active = True
                        for e in enemies: e.kill()
                        boss = Boss(boss_spawn_count)
                        allsprites.add(boss)
                        boss_group.add(boss)
                        next_boss_score += 10000

            #Collisions
            #Normal Enemies
            hits = pygame.sprite.groupcollide(enemies, cures, False, True)
            for enemy, bullets in hits.items():
                player.add_ult(1)
                if enemy.take_hit():
                    player.score += enemy.score_val
                    player.add_ult(enemy.ult_val)
                    stats_manager.update_stat("kill_count", 1)

            ult_hits = pygame.sprite.groupcollide(enemies, ult_slash, False, False)
            for enemy, slashs in ult_hits.items():
                if enemy.take_hit(damage=25):
                    player.score += enemy.score_val
                    player.add_ult(enemy.ult_val)
                    stats_manager.update_stat("kill_count", 1)

            #Boss Collisions
            if boss_active:
                #Normal bullets vs Boss collision (Existing code)
                boss_hits = pygame.sprite.groupcollide(boss_group, cures, False, True)
                for boss_, bullets in boss_hits.items():
                    player.add_ult(1)
                    boss_.hp -= len(bullets)
                    boss_.last_hit_time = pygame.time.get_ticks()
                    if boss_.hp <= 0:
                        player.bonus_score += 5000
                        boss_.kill()
                        boss_active = False
                        player.life = 100
                        for bullet in boss_bullets: bullet.kill()
                        boss_spawn_count += 1
                        boss_theme.stop()

                        pygame.mixer.music.load('Assets/sound/Retro-Battle-Loop.ogg')
                        pygame.mixer.music.set_volume(0.6)
                        pygame.mixer.music.play(-1)
                        current_track = "gameplay"


                #Ult vs Boss
                ult_boss_hits = pygame.sprite.groupcollide(boss_group, ult_slash, False, False)
                for boss_ult_condition, slashes in ult_boss_hits.items():
                    #Now this code will actually run!
                    boss_died = boss_ult_condition.take_hit_from_ult(damage=25)

                    if boss_died:
                        player.bonus_score += 5000
                        boss_ult_condition.kill()
                        boss_active = False
                        player.life = 100
                        for bullet in boss_bullets: bullet.kill()
                        boss_spawn_count += 1

                        boss_theme.stop()
                        pygame.mixer.music.load('Assets/sound/Retro-Battle-Loop.ogg')
                        pygame.mixer.music.set_volume(0.6)
                        pygame.mixer.music.play(-1)
                        current_track = "gameplay"

            #Boss Bullets vs Player and bullets
            pygame.sprite.groupcollide(boss_bullets, cures, True, True)
            pygame.sprite.groupcollide(boss_bullets, ult_slash, True, False)
            if pygame.sprite.spritecollide(player, boss_bullets, True):
                player.take_damage(10)

            #Item Spawning
            now = pygame.time.get_ticks()
            if now - last_item_spawn > 5000:
                last_item_spawn = now
                if random.random() > 0.3:
                    item = Item(random.choice(['heal', 'double_atk', 'firerate', 'shield']))
                    allsprites.add(item)
                    items.add(item)

            #Clean after boss dead
            if not boss_active and len(enemies) < 8: spawn_new_enemy()

            if pygame.sprite.spritecollide(player, enemies, True):
                player.take_damage(10)
                spawn_new_enemy()

            #Item receives
            for hit in pygame.sprite.spritecollide(player, items, True):
                if hit.type == 'heal':
                    heal_sound.play()
                    player.life = min(100, player.life + 20)

                elif hit.type == 'double_atk':
                    double_attack_sound.play()
                    player.activate_double_attack()

                elif hit.type == 'firerate':
                    speed_up_attack_sound.play()
                    player.activate_rapid_fire()

                elif hit.type == 'shield':
                    shield_buff_sound.play()
                    player.has_shield = True

            #Death trigger
            if player.life <= 0:
                pygame.mixer.music.stop()
                boss_theme.stop()
                game_over.play()
                if not stats_saved:
                    stats_manager.update_stat("die_count", 1)
                    stats_manager.update_stat("top_score", player.score + player.bonus_score, cumulative=False)
                    stats_manager.update_stat("max_boss_lvl", boss_spawn_count, cumulative=False)
                    stats_saved = True
                current_state = STATE_GAMEOVER

        #3. DRAW SPRITES & UI (Notice this is outside the `if player.life > 0` check)
        allsprites.draw(screen)

        #UI: Health Bar
        bar_w = 200
        hp_fill = max(0, (player.life / 100) * 200)
        pygame.draw.rect(screen, (50, 0, 0), (10, 10, 200, 20))
        pygame.draw.rect(screen, (0, 255, 0), (10, 10, hp_fill, 20))

        #UI: Ult Bar
        current_charge = min(player.ult_charge, 100)
        ult_fill = (current_charge / 100) * 200

        #Default bar color
        bar_color = (255, 255, 0)

        #2. Logic to change color if full
        if player.ult_charge >= 100:
            bar_color = (0, 255, 255) #Cyan when full

            #Sound Logic
            if not ult_ready_sound_played:
                ultimate_full_sound.play()
                ult_ready_sound_played = True

        #Reset sound trigger if charge drops
        if player.ult_charge < 100:
            ult_ready_sound_played = False

        #3. DRAW THE BARS FIRST (Background)
        #Background bar (Gray)
        pygame.draw.rect(screen, (50, 50, 50), (10, 35, 200, 10))
        #Foreground bar (The colored fill)
        pygame.draw.rect(screen, bar_color, (10, 35, ult_fill, 10))

        #4. DRAW THE TEXT LAST (Foreground)
        #Now the text will appear ON TOP of everything else
        if player.ult_charge >= 100:
            #Main Text
            draw_text(screen, "PRESS Z", 20, 10 + 100, 35, (255, 255, 255))

        #UI: Buffs
        buff_x = 10
        buff_y = 50

        #I fixed the indentation on these buff checks so they all run independently!
        if player.double_attack:
            draw_buff_icon(screen, icon_double, buff_x, buff_y, player.double_attack_duration,
                           player.double_attack_end)
            buff_x += 35

        if player.rapid_fire:
            draw_buff_icon(screen, icon_fire, buff_x, buff_y, player.rapid_fire_duration, player.rapid_fire_end)
            buff_x += 35

        if player.has_shield:
            scaled_shield = pygame.transform.scale(icon_shield, (30, 30))
            screen.blit(scaled_shield, (buff_x, buff_y))
            pygame.draw.rect(screen, (0, 255, 255), (buff_x, buff_y, 30, 30), 2)
            buff_x += 35
            #Draw actual circle around player
            pygame.draw.circle(screen, (0, 200, 255), player.rect.center, 50, 2)

        if boss_active:
            draw_boss_hp(screen, boss)

        draw_text(screen, f"Score: {player.score}", 30, WIDTH - 10, 10, align="right")
        if player.bonus_score > 0:
            draw_text(screen, f"+{player.bonus_score}", 25, WIDTH - 10, 40, (255, 215, 0), align="right")

    elif current_state == STATE_GUIDE:
        #Draw animated background
        screen.blit(menu_bg_frames[bg_current_frame], (0, 0))

        #Dim the background for readability
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        #Title
        draw_text(screen, "GAME GUIDE", 50, WIDTH // 2, 30, (255, 215, 0))

        #Mission Section
        draw_text(screen, "- MISSION -", 30, WIDTH // 2, 90, (255, 100, 100))
        desc_line1 = "As the Thailand Sphere, your mission is to cure the world of COVID-19."
        desc_line2 = "Every 10,000 points, a elite enemy will appear!!!"
        draw_text(screen, desc_line1, 22, WIDTH // 2, 125, (255, 255, 255))
        draw_text(screen, desc_line2, 22, WIDTH // 2, 150, (255, 255, 255))

        #Controls Section
        draw_text(screen, "- CONTROLS -", 30, WIDTH // 2, 200, (100, 200, 255))
        draw_text(screen, "Arrows: Move  |  Space: Attack  |  Z: Ultimate", 24, WIDTH // 2, 235)

        #Items & Buffs Section
        draw_text(screen, "- ITEMS & BUFFS -", 30, WIDTH // 2, 290, (100, 200, 255))
        icon_x = WIDTH // 2 - 160
        text_x = WIDTH // 2 + 20
        start_y = 330
        gap = 55
        icon_size = (35, 35)
        buffs = [
            (icon_heal, "Heal: Restores 20 HP"),
            (icon_double, "Double Shot: Twin projectiles"),
            (icon_fire, "Rapid Fire: Faster attacks"),
            (icon_shield, "Shield: Block 1 hit")
        ]

        for i, (icon, desc) in enumerate(buffs):
            current_y = start_y + (i * gap)
            scaled_icon = pygame.transform.scale(icon, icon_size)
            screen.blit(scaled_icon, (icon_x, current_y))
            draw_text(screen, desc, 22, text_x, current_y + 10)

        #Back Button
        if draw_button(btn_back, 560, STATE_MENU):
            current_state = STATE_MENU


    elif current_state == STATE_PAUSE:
        #1. Keep the background and sprites visible (but frozen)
        screen.blit(bg_gameplay, (0, bg_y1))
        screen.blit(bg_gameplay, (0, bg_y2))
        allsprites.draw(screen)

        #2. Add a dimming overlay
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))  #Black with transparency
        screen.blit(overlay, (0, 0))

        #3. Draw Pause Text and Buttons
        draw_text(screen, "GAME PAUSED", 60, WIDTH // 2, HEIGHT // 2 - 100, (255, 255, 0))
        if draw_button(btn_resume, HEIGHT // 2, STATE_PLAY):
            current_state = STATE_PLAY
        if draw_button(btn_return_to_menu, HEIGHT // 2 + 70, STATE_MENU):
            boss_theme.stop()
            current_state = STATE_MENU
            current_track = "none"


    elif current_state == STATE_GAMEOVER:
        #1. Background and Overlay
        screen.blit(bg_gameplay, (0, bg_y1))  #Use your scrolling BG variables
        screen.blit(bg_gameplay, (0, bg_y2))
        allsprites.draw(screen)
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        #2. Main Title (You can use draw_title if you have a "Game Over" logo)
        draw_text(screen, "GAME OVER", 80, WIDTH // 2, HEIGHT // 2 - 120, (255, 50, 50))

        #3. Use Buttons instead of text
        #Restart button
        if draw_button(btn_restart, HEIGHT // 2, STATE_PLAY):
            pygame.mixer.music.load('Assets/sound/Retro-Battle-Loop.ogg')
            pygame.mixer.music.set_volume(0.6)
            reset_game()
            stats_saved = False
            current_state = STATE_PLAY

            pygame.mixer.music.load('Assets/sound/Retro-Battle-Loop.ogg')
            pygame.mixer.music.set_volume(0.6)
            pygame.mixer.music.play(-1)
            boss_theme.stop()  #Ensure boss music is definitely stopped
            current_track = "gameplay"

        #Return to menu button
        if draw_button(btn_return_to_menu, HEIGHT // 2 + 80, STATE_MENU):
            current_state = STATE_MENU
            pygame.mixer.music.load('Assets/sound/Pixel-Run.ogg')
            pygame.mixer.music.set_volume(0.5)
            pygame.mixer.music.play(-1)

    pygame.display.flip()

pygame.quit()