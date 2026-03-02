import pygame

pygame.init()

screen = pygame.display.set_mode((800, 600))


moon_image = pygame.image.load('../../images/moon.png').convert_alpha()

running = True
x = 0
clock = pygame.time.Clock()

delta_time = 0.1

while running:
    screen.fill((255,255,255))

    screen.blit(moon_image, (x, 0))
    x += 50 * delta_time
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    pygame.display.flip()

    delta_time = clock.tick(60)/1000
    delta_time = max(0.001, min(0.1, delta_time))

pygame.quit()