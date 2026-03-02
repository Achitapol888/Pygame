import pygame, sys

pygame.init()

size = (500,500)

screen = pygame.display.set_mode(size)

pygame.display.set_caption("Meow")
ball = pygame.image.load("../../images/intro_ball.gif")
ballreact = ball.get_rect()
speed = [0,0]
clock = pygame.time.Clock()

while True:

    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_LEFT:
            speed[0] = -abs(speed[0]) + 50
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_RIGHT:
            speed[0] = abs(speed[0])  + 50
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_PLUS:
            speed[1] = -abs(speed[1]) + 50
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_MINUS:
            speed[1] = abs(speed[1])  + 50
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_KP_ENTER:
            speed = [1,1]
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE :
            if speed[0] != 0 and speed[1] != 0:
                speed = [0,0]

        print(speed)

    ballreact = ballreact.move(speed)
    if ballreact.left < 0 or ballreact.right > screen.get_width():
        speed[0] = -speed[0]
    elif ballreact.top < 0 or ballreact.bottom > screen.get_height():
        speed[1] = -speed[1]



    screen.fill("white")
    screen.blit(ball, ballreact)
    pygame.display.flip()


