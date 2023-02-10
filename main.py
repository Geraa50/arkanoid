import pygame
from random import randrange as rnd


WIDTH, HEIHTN = 1200, 800
fps = 60
platform_width = 330
platform_height = 35
platform_speed = 15
platforma = pygame.Rect(WIDTH // 2 - platform_width // 2, HEIHTN - platform_height - 10,
                        platform_width, platform_height)
charik_raduis = 20
charick_speed = 6
charick_rect = int(charik_raduis * 2 ** 0.5)
ball = pygame.Rect(WIDTH // 2, HEIHTN - platform_height - 100, charick_rect, charick_rect)
napravl_x, napravl_y = 1, -1
kirpichi = [pygame.Rect(1 + 55 * i, 1 + 30 * j, 50, 25) for i in range(100) for j in range(10)]
start_game = False


pygame.init()
sc = pygame.display.set_mode((WIDTH, HEIHTN))
clock = pygame.time.Clock()
img = pygame.image.load('1.jpg').convert()
# фон добавить надо любой


def detect_collision(dx, dy, ball, rect):
    if dx > 0:
        delta_x = ball.right - rect.left
    else:
        delta_x = rect.right - ball.left
    if dy > 0:
        delta_y = ball.bottom - rect.top
    else:
        delta_y = rect.bottom - ball.top

    if abs(delta_x - delta_y) < 10:
        dx, dy = -dx, -dy
    elif delta_x > delta_y:
        dy = -dy
    elif delta_y > delta_x:
        dx = -dx
    return dx, dy


while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()
    sc.blit(img, (0, 0))
    [pygame.draw.rect(sc, 'green', kirpich) for c, kirpich in enumerate(kirpichi)]
    pygame.draw.rect(sc, pygame.Color('darkblue'), platforma)
    pygame.draw.circle(sc, pygame.Color('white'), ball.center, charik_raduis)

    mouse_x, mouse_y = pygame.mouse.get_pos()
    platforma.left = mouse_x - 165

    if event.type == pygame.MOUSEBUTTONDOWN or start_game:
        start_game = True
        pygame.mouse.set_visible(False)
    else:
        pygame.display.flip()
        pygame.mouse.set_pos(WIDTH // 2, HEIHTN // 2)
        pygame.mouse.set_visible(True)
        continue

    ball.x += charick_speed * napravl_x
    ball.y += charick_speed * napravl_y

    if ball.centerx < charik_raduis or ball.centerx > WIDTH - charik_raduis:
        napravl_x *= -1
    if ball.centery < charik_raduis:
        napravl_y *= -1
    if ball.colliderect(platforma) and napravl_y > 0:
        napravl_x, napravl_y = detect_collision(napravl_x, napravl_y, ball, platforma)
    # Надо добавить разные коэффициенты на касания с разными частями платформы чем ближе к центру тем прямее отскок
    # А то получается оно как отсутствие двд диска прыгает запрограммировано
    number_kirpich_delete = ball.collidelist(kirpichi)
    if number_kirpich_delete != -1:
        delete_kirpich = kirpichi.pop(number_kirpich_delete)
        napravl_x, napravl_y = detect_collision(napravl_x, napravl_y, ball, delete_kirpich)
        # Без строки выше играть интереснее ;)

    if ball.bottom > HEIHTN:
        exit()
    # Добавить победу и более красочное поражение (экран поражения)


    pygame.display.flip()
    clock.tick(fps)
