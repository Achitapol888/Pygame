import sys, pygame                      #import pygame library
pygame.init()                                #initial pygame system

size = width, height = 640, 640 #variable to set size of window
speed = [1, 1]                              # x y speed
black = 0, 0, 0                             #define black color
red = 255,0,0
screen = pygame.display.set_mode(size)   #intitalize screen -> surface
pygame.display.set_caption("Show FPS")
font = pygame.font.SysFont("robotto", 24)
ball = pygame.image.load("../../images/intro_ball.gif")  #load image from file
ballrect = ball.get_rect()
clock = pygame.time.Clock()
while 1:
    clock.tick(75)

    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT:
                speed[0] = abs(speed[0])
            if event.key == pygame.K_LEFT:
                speed[0] = -abs(speed[0])
            if event.key == pygame.K_DOWN:
                speed[1] = abs(speed[1])
            if event.key == pygame.K_UP:
                speed[1] = -abs(speed[1])

    ballrect = ballrect.move(speed)
    if ballrect.left < 0 or ballrect.right > width:
        speed = (0,0)
    if ballrect.top < 0 or ballrect.bottom > height:
        speed = (0,0)
    textFps = font.render("FPS: "+str(int(clock.get_fps())), True, red)

    screen.fill(black)
    screen.blit(textFps,(20,20))
    screen.blit(ball, ballrect)
    pygame.draw.rect(screen,red,(0,0,1280,960),10)
    pygame.display.flip()
