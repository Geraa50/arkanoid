import pygame
import sys
import os

WIDTH, HEIGHT = 1200, 600
fps = 60

if __name__ == "__main__":
    pygame.init()
    pygame.display.set_caption('arkanoid')
    screen = pygame.display.set_mode((WIDTH, HEIGHT))


def load_sprite(name, colorkey=None):  # не работает без предварительной инициализации pygame
    # если файл не существует, то выходим
    if not os.path.isfile(name):
        print(f"Файл с изображением '{name}' не найден")
        sys.exit()
    image = pygame.image.load(name)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


allBrickSprites = pygame.sprite.Group()


class Brick(pygame.sprite.Sprite):
    image = load_sprite("sprites/brick_blue.png")

    def __init__(self, x, y):
        super().__init__(allBrickSprites)
        self.image = Brick.image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def return_brick(self):
        return self.rect


class BrickManager:
    def __init__(self, left, top, kol_vo_w, kol_vo_h):
        self.bricks = [Brick(1 + left * i, 1 + top * j)
                       for i in range(kol_vo_w) for j in range(kol_vo_h)]

    def delete_brick(self, number_brick_which_delete):
        brick = self.bricks.pop(number_brick_which_delete)
        allBrickSprites.remove(brick) 
        return brick

    def get_bricks_list(self):
        return self.bricks

    def detect_finish(self):
        if self.bricks:
            return False
        else:
            return True

    def get_brick_quantity(self):
        return len(self.bricks)


platformSprite = pygame.sprite.Group()


class Platform(pygame.sprite.Sprite):
    image = load_sprite("sprites/platform.png")

    def __init__(self, w, h, s):
        super().__init__(platformSprite)
        self.x, self.y = 0, 0
        self.rect_width = w
        self.rect_height = h
        self.rect_speed = s
        self.image = Platform.image
        self.rect = pygame.Rect(WIDTH // 2 - self.rect_width // 2, HEIGHT - self.rect_height - 10,
                                self.rect_width, self.rect_height)

    def move_platform(self, coord_mouse):
        self.x, self.y = coord_mouse
        self.rect.left = self.x - 165

    def collide_with_platform(self, ball):
        return ball.colliderect(self.rect)

    def return_platform(self):
        return self.rect

    def return_height(self):
        return self.rect_height


ballSprite = pygame.sprite.Group()


class Ball(pygame.sprite.Sprite):
    anim_sprites = [load_sprite(f"sprites/ball_anim/ball_anim{_}.png") for _ in range(1, 10)]

    def __init__(self, r, s):
        super().__init__(ballSprite)
        self.rect_raduis = r
        self.rect_speed = s
        self.rect_rect = int(self.rect_raduis * 2 ** 0.5)
        self.direction_x, self.direction_y = 1, -1
        self.image = Ball.anim_sprites[0]
        self.rect = pygame.Rect(WIDTH // 2, HEIGHT - 35 - 100, self.rect_rect, self.rect_rect)

        self.current_frame = 0
        self.frame_delay = 0
        self.is_animate = False


    def movement_ball(self):
        self.rect.x += self.rect_speed * self.direction_x
        self.rect.y += self.rect_speed * self.direction_y

    def change_direction(self):
        if self.rect.centerx < self.rect_raduis or self.rect.centerx > WIDTH - self.rect_raduis:
            self.direction_x *= -1
        if self.rect.centery < self.rect_raduis:
            self.direction_y *= -1

    def collide_with_platform(self, rect):
        if self.rect.colliderect(rect):
            print("ball colided with platform")
            self.is_animate = True
            return True
        return False

    def return_ball(self):
        return self.rect

    def return_direction_y(self):
        return self.direction_y

    def change_direction_with_brick(self, deleted):
        self.direction_x, self.direction_y = detect_collision(self.direction_x, self.direction_y, self.rect, deleted)

    def change_direction_with_platform(self, platform):
        self.direction_x, self.direction_y = detect_collision(self.direction_x, self.direction_y, self.rect, platform)
        # Надо добавить разные коэффициенты на касания с разными частями платформы чем ближе к центру тем прямее отскок
        # А то получается оно как отсутствие двд диска прыгает запрограммировано

    def update(self, delta):
        self.frame_delay += delta
        if self.frame_delay > 0.02:
            if self.is_animate:
                if self.current_frame == 9:
                    self.image = Ball.anim_sprites[0]
                    self.current_frame = 0
                    self.is_animate = False
                    return
                self.image = Ball.anim_sprites[self.current_frame]
                self.current_frame += 1
                self.frame_delay = 0



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


def terminate():
    pygame.quit()
    sys.exit()


def game_field_init():
    """return BrickManager, Platform, Ball"""
    global allBrickSprites, platformSprite, ballSprite
    if allBrickSprites:
        for _ in allBrickSprites:
            allBrickSprites.remove(_)
    if platformSprite:
        for _ in platformSprite:
            platformSprite.remove(_)
    if ballSprite:
        for _ in ballSprite:
            ballSprite.remove(_)
    return BrickManager(55, 30, 10, 2), Platform(330, 35, 15), Ball(20, 6)


font = pygame.font.Font('fonts/Pentapixel.ttf', 33)


def start_screen():
    global font
    start_fps = 1
    intro_text = ['Press any key to start game']

    fon = pygame.image.load('windows/start_game.png').convert()
    fon = pygame.transform.scale(fon, (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
    red_or_blue = 0
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return  # начинаем игру
        for line in intro_text:
            if red_or_blue:
                string_rendered = font.render(line, True, pygame.Color('blue'))
                red_or_blue = 0
            else:
                string_rendered = font.render(line, True, pygame.Color('red'))
                red_or_blue = 1
            intro_rect = string_rendered.get_rect()
            screen.blit(string_rendered, intro_rect)
        pygame.display.flip()
        clock.tick(start_fps)


def finish_screen(score):
    global font
    start_fps = 1
    intro_text = [f' Victory!{" " * 50}your score:{score}{" " * 22}Press any key to restart game']

    fon = pygame.image.load('windows/finish_window_v2_version.png').convert()
    fon = pygame.transform.scale(fon, (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
    red_or_blue = 0
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return game_field_init() 
        for line in intro_text:
            if red_or_blue:
                string_rendered = font.render(line, True, pygame.Color('red'))
                red_or_blue = 0
            else:
                string_rendered = font.render(line, True, pygame.Color('yellow'))
                red_or_blue = 1
            intro_rect = string_rendered.get_rect()
            screen.blit(string_rendered, intro_rect)
        pygame.display.flip()
        clock.tick(start_fps)


def game_over_screen():
    global font
    start_fps = 1
    intro_text = [f'   Game Over!{" " * 76}Press any key to restart game']

    fon = pygame.image.load('windows/finish_window_v3.png').convert()
    fon = pygame.transform.scale(fon, (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
    red_or_blue = 0
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return game_field_init()
        for line in intro_text:
            if red_or_blue:
                string_rendered = font.render(line, True, pygame.Color('blue'))
                red_or_blue = 0
            else:
                string_rendered = font.render(line, True, pygame.Color('red'))
                red_or_blue = 1
            intro_rect = string_rendered.get_rect()
            screen.blit(string_rendered, intro_rect)
        pygame.display.flip()
        clock.tick(start_fps)


if __name__ == '__main__':
    clock = pygame.time.Clock()
    img = pygame.image.load('windows/1.jpg').convert()
    start_screen()
    running = True
    start_game = True
    game_field_init()
    bricks_quantity_w = 20
    bricks_quantity_h = 10
    bricks_quantity = bricks_quantity_w * bricks_quantity_w
    bricks, platform, ball = game_field_init()
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                start_game = True
                pygame.mouse.set_visible(False)

        if start_game:
            delta = clock.tick(fps) / 1000

            screen.blit(img, (0, 0))
            allBrickSprites.draw(screen)
            platformSprite.draw(screen)
            ball.update(delta)
            ballSprite.draw(screen)

            platform.move_platform(pygame.mouse.get_pos())

            pygame.display.flip()
            # pygame.mouse.set_pos(WIDTH // 2, HEIGHT // 2)
            pygame.mouse.set_visible(True)

            ball.movement_ball()
            ball.change_direction()
            if ball.collide_with_platform(platform.return_platform()) and ball.return_direction_y() > 0:
                ball.change_direction_with_platform(platform.return_platform())
            number_brick_delete = ball.return_ball().collidelist(bricks.get_bricks_list())
            if number_brick_delete != -1:
                deleted_brick = bricks.delete_brick(number_brick_delete).return_brick()
                ball.change_direction_with_brick(deleted_brick)

            if bricks.detect_finish():
            # if True:
                bricks, platform, ball = finish_screen(bricks_quantity)
            if ball.return_ball().bottom > HEIGHT:
                bricks, platform, ball = game_over_screen()

            pygame.display.flip()
    pygame.quit()
