import pygame
import os

from load_sprite import load_sprite

allBrickSprites = pygame.sprite.Group()


class Brick(pygame.sprite.Sprite):
    image = load_sprite('sprites/brick_blue.png')

    def __init__(self, x, y, image):
        super().__init__(allBrickSprites)
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def return_brick(self):
        return self.rect


class BrickMapLoader:
	brick_dict = {
	'B': load_sprite('sprites/brick_blue.png'),
	'G': load_sprite('sprites/brick_deep_green.png'),
	'g': load_sprite('sprites/brick_green.png'),
	'b': load_sprite('sprites/brick_light_blue.png'),
	'o': load_sprite('sprites/brick_orange.png'),
	'p': load_sprite('sprites/brick_pink.png'),
	'r': load_sprite('sprites/brick_red.png'),
	'v': load_sprite('sprites/brick_violet.png'),
	'w': load_sprite('sprites/brick_white.png'),
	'y': load_sprite('sprites/brick_yellow.png'),

	}

	def generate_default_gamefield(left, top, count_w, count_h):
		return [Brick(1 + left * i, 1 + top * j, BrickMapLoader.brick_dict['b']) for i in range(count_w) for j in range(count_h)]

	def __init__(self, file):
		self.step_x = 55
		self.step_y = 30
		if not os.path.isfile(file):
			print(f"Файл с уровнем '{name}' не найден")
			sys.exit()

		with open(file, mode='rt') as map_file:
			brick_lines = map_file.readlines()
			bricks = [[brick for brick in brick_line.strip().split(' ')] for brick_line in brick_lines]
			self.brick_map = self.generate_gamefield(bricks)
	
	def get_brick_map(self):
		return self.brick_map

	def generate_gamefield(self, bricks):
		brick_map = []
		for brick_line in range(len(bricks)):
			for brick in range(len(bricks[brick_line])):
				current_brick = bricks[brick_line][brick]
				if current_brick == '-':
					continue
				brick_map.append(Brick(self.step_x * brick, self.step_y * brick_line, self.brick_dict[current_brick]))
		return brick_map


class BrickManager:
    def __init__(self, bricks):
        self.bricks = bricks

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




