import pygame
from random import randrange as rnd


WIDTH, HEIHTN = 1200, 800
fps = 60
# platform_width = 330
platform_height = 35
# platform_speed = 15
# platforma = pygame.Rect(WIDTH // 2 - platform_width // 2, HEIHTN - platform_height - 10,
#                         platform_width, platform_height)
charik_raduis = 20
charick_speed = 6
charick_rect = int(charik_raduis * 2 ** 0.5)
ball = pygame.Rect(WIDTH // 2, HEIHTN - platform_height - 100, charick_rect, charick_rect)
napravl_x, napravl_y = 1, -1
# kirpichi = [pygame.Rect(1 + 55 * i, 1 + 30 * j, 50, 25) for i in range(100) for j in range(10)]
#  kirpichi = [pygame.Rect(1 + 55 * i, 1 + 30 * j, 1200, 25) for i in range(1) for j in range(1)]
#  включить строку сверху и выключить строку над ней, что бы получить один большой кирпич, для проверки окончания игры
# До начала программы прописать kirpichi(все значения)б потом прописывать их рендер вместо draw и
# delete через класс, а не сразу


class Kirpichi:
    def __init__(self, left, top, size_w, size_h, kol_vo_w, kol_vo_h):
        self.kirpichi = [pygame.Rect(1 + left * i, 1 + top * j, size_w, size_h)
                         for i in range(kol_vo_w) for j in range(kol_vo_h)]

    def delete_kirpich(self, number_kirpich_which_delete):
        return self.kirpichi.pop(number_kirpich_which_delete)
    
    def render_kirpichi(self, sc):
        [pygame.draw.rect(sc, 'green', kirpich) for c, kirpich in enumerate(self.kirpichi)]

    def kirpichi_list(self):
        return self.kirpichi


class Platforma:
    def __init__(self, w, h, s):
        self.x, self.y = 0, 0
        self.platform_width = w
        self.platform_height = h
        self.platform_speed = s
        self.platforma = pygame.Rect(WIDTH // 2 - self.platform_width // 2, HEIHTN - self.platform_height - 10,
                                     self.platform_width, self.platform_height)

    def move_platform(self, coord_mouse):
        self.x, self.y = coord_mouse
        self.platforma.left = self.x - 165

    def collide_with_platforma(self):
        return ball.colliderect(self.platforma)

    def render_platform(self, sc):
        pygame.draw.rect(sc, pygame.Color('darkblue'), self.platforma)

    def return_platfroma(self):
        return self.platforma


class Ball:
    def __init__(self):
        self.ball = pygame.Rect(WIDTH // 2, HEIHTN - platform_height - 100, charick_rect, charick_rect)

    def movement_ball(self, speed, x, y):
        ball.x += speed * x
        ball.y += speed * y

    def change_napravl(self):
        pass

    def colision_ball(self):
        pass

    def ball_position_x(self):
        pass

    def ball_posotion_y(self):
        pass

    def return_ball(self):
        return self.ball


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


if __name__ == '__main__':
    pygame.init()
    pygame.display.set_caption('arkanoid')
    sc = pygame.display.set_mode((WIDTH, HEIHTN))
    clock = pygame.time.Clock()
    img = pygame.image.load('1.jpg').convert()
    runniing = True
    start_game = False
    # фон добавить надо любой
    kirpichi = Kirpichi(55, 30, 50, 25, 100, 10)
    pltfrm = Platforma(330, 35, 15)
    while runniing:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                runniing = False
        sc.blit(img, (0, 0))
        kirpichi.render_kirpichi(sc)
        pltfrm.render_platform(sc)
        # pygame.draw.rect(sc, pygame.Color('darkblue'), platforma)
        pygame.draw.circle(sc, pygame.Color('white'), ball.center, charik_raduis)
        pltfrm.move_platform(pygame.mouse.get_pos())
        # mouse_x, mouse_y = pygame.mouse.get_pos()
        # platforma.left = mouse_x - 165

        if event.type == pygame.MOUSEBUTTONDOWN or start_game:
            start_game = True
            pygame.mouse.set_visible(False)
        else:
            pygame.display.flip()
            pygame.mouse.set_pos(WIDTH // 2, HEIHTN // 2)
            pygame.mouse.set_visible(True)
            continue
        class_ball = Ball()
        class_ball.movement_ball(charick_speed, napravl_x, napravl_y)
        # ball.x += charick_speed * napravl_x
        # ball.y += charick_speed * napravl_y
        if ball.centerx < charik_raduis or ball.centerx > WIDTH - charik_raduis:
            napravl_x *= -1
        if ball.centery < charik_raduis:
            napravl_y *= -1
        if pltfrm.collide_with_platforma() and napravl_y > 0:
            napravl_x, napravl_y = detect_collision(napravl_x, napravl_y, ball, pltfrm.return_platfroma())
    # Надо добавить разные коэффициенты на касания с разными частями платформы чем ближе к центру тем прямее отскок
    # А то получается оно как отсутствие двд диска прыгает запрограммировано
        number_kirpich_delete = ball.collidelist(kirpichi.kirpichi_list())
        if number_kirpich_delete != -1:
            deleted_kirpich = kirpichi.delete_kirpich(number_kirpich_delete)
            napravl_x, napravl_y = detect_collision(napravl_x, napravl_y, ball, deleted_kirpich)
        # Без строки выше играть интереснее ;)

        if ball.bottom > HEIHTN:
            exit()
    # Добавить победу и более красочное поражение (экран поражения)

        pygame.display.flip()
        clock.tick(fps)
