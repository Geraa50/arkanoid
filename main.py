import pygame
from settings import HOST
from GameClient import ISynchronizedObject, GameTCPClient
# нужно модуль loguru поставить чтоб логи заработали
from loguru import logger
logger.add("file.log", backtrace=True, diagnose=True, enqueue=True) 


allPlatforms = pygame.sprite.Group()
ballSprite = pygame.sprite.Group()
WIDTH, HEIGHT = 1200, 600
fps = 60


class BrickManager():
    def __init__(self, left, top, size_w, size_h, kol_vo_w, kol_vo_h):
        self.bricks = [pygame.Rect(1 + left * i, 1 + top * j, size_w, size_h)
                         for i in range(kol_vo_w) for j in range(kol_vo_h)]

    def delete_brick(self, number_brick_which_delete):
        return self.bricks.pop(number_brick_which_delete)
    
    def render_bricks(self, screen):
        [pygame.draw.rect(screen, 'green', brick) for c, brick in enumerate(self.bricks)]

    def get_bricks_list(self):
        return self.bricks


class Platform(pygame.sprite.Sprite, ISynchronizedObject):
    def __init__(self, w, h, s):
        ISynchronizedObject.__init__(self)
        super().__init__(allPlatforms)
        self.x, self.y = 0, 0
        self.platform_width = w
        self.platform_height = h
        self.platform_speed = s
        self.rect = pygame.Rect(WIDTH // 2 - self.platform_width // 2, HEIGHT - self.platform_height - 10,
                                self.platform_width, self.platform_height)
        self.image = pygame.Surface((w, h))
        pygame.draw.rect(self.image, pygame.Color('darkblue'), (0, 0, w, h))

    @staticmethod
    def getInitSyncObjectData(packageDict):
        init_dict = {"w": 330, "h": 35, "s": 15}
        return init_dict

    def returnPackingData(self):
        return {"x": self.rect.x}

    def setPackingData(self, data):
        self.rect.x = data["x"]

    # def move_platform(self, coord_mouse):
    #     self.x, self.y = coord_mouse
    #     self.platform.left = self.x - 165

    def collide_with_platform(self, ball):
        return ball.colliderect(self.rect)
        
    def return_platform(self):
        return self.rect

    def return_height(self):
        return self.platform_height

    def remove(self):
        for _ in self.groups():
            _.remove(self)

    def update(self, mousepos):
        self.rect.x = mousepos[0]
    

class Ball(pygame.sprite.Sprite, ISynchronizedObject):
    def __init__(self, r, s):
        ISynchronizedObject.__init__(self)
        super().__init__(ballSprite)
        self.ball_raduis = r
        self.ball_speed = s
        self.ball_rect = int(self.ball_raduis * 2 ** 0.5)
        self.direction_x, self.direction_y = 1, -1
        self.rect = pygame.Rect(WIDTH // 2, HEIGHT - 35 - 100, self.ball_rect, self.ball_rect)
        self.image = pygame.Surface((r * 2, r * 2))
        pygame.draw.circle(self.image, pygame.Color('white'), (r, r), r)

    def setPackingData(self, data):
        if data:
            self.rect.x, self.rect.y = data[0], data[1]

    def movement_ball(self):
        self.rect.x += self.ball_speed * self.direction_x
        self.rect.y += self.ball_speed * self.direction_y

    def change_direction(self):
        if self.rect.centerx < self.ball_raduis or self.rect.centerx > WIDTH - self.ball_raduis:
            self.direction_x *= -1
        if self.rect.centery < self.ball_raduis:
            self.direction_y *= -1

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
    client = GameTCPClient(HOST, globals(), globalsEnabled=True)
    client.start()
    client.isInitDone.wait()


    pygame.init()
    pygame.display.set_caption('arkanoid')
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    img = pygame.image.load('1.jpg').convert()
    running = True
    start_game = False
    # фон добавить надо любой
    bricks = BrickManager(55, 30, 50, 25, 100, 10)
    platform = client.synchronize(Platform, None, w=330, h=35, s=15)
    # platform = Platform(330, 35, 15)
    ball = client.synchronize(Ball, "Ball", r=20, s=6)
    # ball = Ball(20, 6)
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                start_game = True
                pygame.mouse.set_visible(False)

        if start_game:
            clock.tick(fps)
            package = client.getPackage()
            if package:
                client.processPackage(package)


            screen.blit(img, (0, 0))
            bricks.render_bricks(screen)
            ballSprite.draw(screen)

            allPlatforms.draw(screen)
            platform.update(pygame.mouse.get_pos())

        
            pygame.display.flip()
            # pygame.mouse.set_pos(WIDTH // 2, HEIGHT // 2)
            pygame.mouse.set_visible(True)


            # ball.movement_ball()
            ball.change_direction()
            if platform.collide_with_platform(ball.return_ball()) and ball.return_direction_y() > 0:
                ball.change_direction_with_platform(platform.return_platform())

            number_brick_delete = ball.return_ball().collidelist(bricks.get_bricks_list())
            if number_brick_delete != -1:
                deleted_brick = bricks.delete_brick(number_brick_delete)
                ball.change_direction_with_brick(deleted_brick)

            # if ball.return_ball().bottom > HEIGHT:
            #     running = False

           # Добавить победу и более красочное поражение (экран поражения)

            pygame.display.flip()
            client.donePackage()            
    pygame.quit()
    client.close()