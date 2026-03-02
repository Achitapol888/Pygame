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
# g

#game cycle
going = 1
while going:
    clock.tick(FPS)
    #input
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            going = 0


    #process

    #output
    pygame.display.flip()

pygame.quit()
