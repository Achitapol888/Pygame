import random
import pygame

#Setup screen
WIDTH = 600
HEIGHT = 800
FPS = 60
pygame.init()
screen = pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption("Covid-19 War")
font = pygame.font.SysFont("robotto", 40, bold=True)
clock = pygame.time.Clock()
running = 1
pygame.mixer.init()
boom_sound = pygame.mixer.Sound("boom.wav")

#Classes
class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.playerImages = [pygame.image.load("JiJiSR1.png").convert_alpha(),
                             pygame.image.load("JiJiSR1L.png").convert_alpha(),
                             pygame.image.load("JiJiSR1R.png").convert_alpha()]
        self.image = self.playerImages[0]
        self.rect = self.image.get_rect()
        self.rect.midbottom = WIDTH/2,HEIGHT-20
        self.speedx = 0
        self.lastSpeedx = self.speedx
        self.life  = 100
        self.score = 0

    def update(self):
        self.rect.x += self.speedx
        if (self.lastSpeedx != self.speedx) and (self.speedx < 0):
            self.image = self.playerImages[1]
        elif(self.lastSpeedx != self.speedx) and  (self.speedx > 0):
            self.image = self.playerImages[2]
        elif(self.lastSpeedx != self.speedx) and  (self.speedx == 0):
            self.image = self.playerImages[0]
        self.lastSpeedx = self.speedx
    def shoot(self):
        cure = Cure(self.rect.centerx,self.rect.top)
        allsprites.add(cure)
        cures.add(cure)

class Covid(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        #self.image = pygame.Surface((32,32))
        #self.image.fill((255,0,0))
        self.image = pygame.image.load("covid19.png").convert_alpha()
        self.rect = self.image.get_rect()
        self.reSpawn()
    def reSpawn(self):
        self.rect.x = random.randrange(WIDTH-self.rect.width)
        self.rect.y = random.randrange(-100,-40)
        self.speedx = random.randrange(-2,2)
        self.speedy = random.randrange(1,10)
    def update(self):
        self.rect.x += self.speedx
        self.rect.y += self.speedy
        if self.rect.top > HEIGHT+10:
            self.reSpawn()
class Cure(pygame.sprite.Sprite):
    def __init__(self,x,y):
        pygame.sprite.Sprite.__init__(self)
        #self.image = pygame.Surface((18,34))
        #self.image.fill((0,255,0))
        self.image = pygame.image.load("cure.png").convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speedy = -10
    def update(self):
        self.rect.y += self.speedy
        if self.rect.bottom < 0:
            self.kill()

player = Player()
allsprites = pygame.sprite.Group()
allsprites.add(player)
cures = pygame.sprite.Group()

covids = pygame.sprite.Group()
for i in range(10):
    c = Covid()
    allsprites.add(c)
    covids.add(c)

while running :
    clock.tick(FPS)
    #input
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = 0
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                player.speedx = -4
            if event.key == pygame.K_RIGHT:
                player.speedx = 4
            if event.key == pygame.K_SPACE:
                player.shoot()

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                player.speedx = 0
            if event.key == pygame.K_RIGHT:
                player.speedx = 0
            if (event.key == pygame.K_RETURN) and (player.life < 0):
                player.score = 0
                player.life = 100

    #process
    allsprites.update()
    playerHit = pygame.sprite.spritecollide(player,covids,False)
    if playerHit:
        player.life -= 1
        boom_sound.play()
    cure_hits = pygame.sprite.groupcollide(covids,cures,True,True)
    for hit in cure_hits:
        c = Covid()
        covids.add(c)
        allsprites.add(c)
        player.score += 100

    #output
    screen.fill((0,0,0))
    pygame.draw.rect(screen,(0,255,255),(10,10,player.life*2,30))
    textScore = font.render("score " + str(player.score), True, (0,255,255))
    screen.blit(textScore,((WIDTH-textScore.get_width())/2, 10))
    if player.life < 0:
        textOver = font.render("Game Over ", True, (0,255,255))
        screen.blit(textOver,((WIDTH-textOver.get_width())/2, HEIGHT/2-50))
        textOver = font.render("Press Enter to try again", True, (0,255,255))
        screen.blit(textOver,((WIDTH-textOver.get_width())/2, HEIGHT/2))
    allsprites.draw(screen)
    pygame.display.flip()
