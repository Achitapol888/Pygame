import os,sys
import pygame
import random
from pygame.compat import geterror

if not pygame.font:
    print("Warning, fonts disabled")
if not pygame.mixer:
    print("Warning, sound disabled")
main_dir = os.path.split(os.path.abspath(__file__))[0]
#data_dir = os.path.join(main_dir, "data")
RED = (255,0,0)
BLACK = (0,0,0)
GREEN = (0,255,0)
FPS = 60
WIDTH = 600
HEIGHT = 800

def load_image(name, colorkey=None):
    #fullname = os.path.join(data_dir, name)
    fullname = name
    try:
        image = pygame.image.load(fullname)
    except pygame.error:
        print("Cannot load image:", fullname)
        raise SystemExit(str(geterror()))
    image = image.convert()
    if colorkey is not None:
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey, pygame.RLEACCEL)
    return image, image.get_rect()

def load_sound(name):
    class NoneSound:
        def play(self):
            pass

    if not pygame.mixer or not pygame.mixer.get_init():
        return NoneSound()
    #fullname = os.path.join(data_dir, name)
    try:
        sound = pygame.mixer.Sound(name)
    except pygame.error:
        print("Cannot load sound: %s" % name)
        raise SystemExit(str(geterror()))
    return sound



class Player(pygame.sprite.Sprite):

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)  # call Sprite initializer
        self.image, self.rect = load_image("JiJiSR1.png")
        self.rect.midbottom = WIDTH/2, HEIGHT-50
        self.speedx = 0

    def update(self):
        self.rect.x += self.speedx
        if self.rect.right >= WIDTH: self.rect.right = WIDTH
        if self.rect.left <= 0: self.rect.left = 0

    def shoot(self):
        bullet = Bullet(self.rect.centerx, self.rect.top)
        allsprites.add(bullet)
        bullets.add(bullet)

class Asteroid (pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((30,40))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.reSpawn()

    def update(self):
        self.rect.x += self.speedx
        self.rect.y += self.speedy
        if self.rect.top > HEIGHT+10:
            self.reSpawn()

    def reSpawn(self):
        self.rect.x = random.randrange(WIDTH-self.rect.width)
        self.rect.y = random.randrange(-100,-40)
        self.speedx = random.randrange(-2,2)
        self.speedy = random.randrange(1,10)

class Bullet(pygame.sprite.Sprite):
    def __init__(self,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((10,20))
        self.rect = self.image.get_rect()
        self.image.fill(GREEN)
        self.rect.centerx = x
        self.rect.bottom = y
        self.speedy = -10
    def update(self):
        self.rect.y += self.speedy
        if self.rect.bottom < 0:
            self.kill()



pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space War")
font = pygame.font.SysFont("robotto", 40, bold=True)
clock = pygame.time.Clock()
score = 0
boom_sound = load_sound("boom.wav")


allsprites = pygame.sprite.Group()
bullets = pygame.sprite.Group()
asteroids = pygame.sprite.Group()

player = Player()
allsprites.add(player)
for i in range(5):
    a = Asteroid()
    allsprites.add(a)
    asteroids.add(a)
life = 100
going = 1
while going:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            going = 0
        if life>0:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    player.speedx = -10
                if event.key == pygame.K_RIGHT:
                    player.speedx = 10
                if event.key == pygame.K_SPACE:
                    player.shoot()
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    player.speedx = 0
                if event.key == pygame.K_RIGHT:
                    player.speedx = 0
                if event.key == pygame.K_SPACE:
                    player.shoot()
        else:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    life = 100
                    score = 0

    allsprites.update()
    player_hits = pygame.sprite.spritecollide(player,asteroids,False)
    if (player_hits):
        life -= 1
        boom_sound.play()
    bullet_hits = pygame.sprite.groupcollide(asteroids, bullets,True,True)
    for hit in bullet_hits:
        a = Asteroid()
        allsprites.add(a)
        asteroids.add(a)
        score += 100

    screen.fill(BLACK)
    allsprites.draw(screen)
    pygame.draw.rect(screen,GREEN,(10,10,life,10))
    textScore = font.render("score " + str(score), True, GREEN)
    screen.blit(textScore,((WIDTH-textScore.get_width())/2, 10))
    if life < 0:
        textOver = font.render("Game Over ", True, RED)
        screen.blit(textOver,((WIDTH-textOver.get_width())/2, HEIGHT/2-50))
        textOver = font.render("Press Enter to try again", True, RED)
        screen.blit(textOver,((WIDTH-textOver.get_width())/2, HEIGHT/2))


    pygame.display.flip()

pygame.quit()
