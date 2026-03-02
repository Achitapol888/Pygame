import os,sys
import pygame

#setup
WIDTH = 640
HEIGHT = 640
FPS = 60
pygame.init()
screen = pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption("Sprite Animation")
clock = pygame.time.Clock()

#game classes and objects
class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.walkSouths = [pygame.image.load("HM_South_Stand.png").convert(),
                          pygame.image.load("HM_South_Walk_Lt.png").convert(),
                          pygame.image.load("HM_South_Walk_Rt.png").convert()]
        self.index = 0
        self.image = self.walkSouths[self.index]
        self.rect = pygame.Rect(0,0,64,64)
        self.dir = 5
        self.lastDir = 5
        self.sit = False
        self.ani_speed = 1
        self.interFrame = 5
        self.attacking = 0
        self.playerSpeed = 4

    def update(self):
        self.ani_speed += 1
        if self.dir == 2:
            self.rect.y += self.playerSpeed
            if self.ani_speed >= self.interFrame:
                self.ani_speed = 1
                self.index +=1
                if self.index >= len(self.walkSouths):
                    self.index =0;
                self.image = self.walkSouths[self.index]



#setup objects
allsprites = pygame.sprite.Group()
player = Player()
allsprites.add(player)


#game cycle
going = 1
while going:
    clock.tick(FPS)
#input
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            going = 0
        if event.type == pygame.KEYDOWN :
            if event.key == pygame.K_DOWN:
                player.dir = 2
        if event.type == pygame.KEYUP:
            player.dir = 5


    #process
    allsprites.update()

    #output
    screen.fill((0,0,0))
    allsprites.draw(screen)
    pygame.display.flip()

pygame.quit()
