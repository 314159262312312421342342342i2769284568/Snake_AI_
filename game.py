import pygame, random, numpy as np
from enum import Enum
from collections import namedtuple
pygame.init(); pygame.mixer.init()
try:
    eating_sound = pygame.mixer.Sound(0)
except:
    eating_sound = None
font = pygame.font.SysFont('Arial', 20, bold=True)
class Direction(Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4
Point = namedtuple('Point', 'x, y')
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
ORANGE = (255, 165, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
PURPLE = (128, 0, 128)
BLUE1 = (0, 0, 255)
BLUE2 = (0, 100, 255)
BROWN = (101, 67, 33)
DARK_BROWN = (60, 40, 20)
GRID_COLOR = (40, 40, 40)
BLOCK_SIZE = 25
APPLE_SIZE = 30
SPEED = 50
WALL_SIZE = 25
HUD_HEIGHT = 50
class SnakeGameAI:
    def __init__(self, w=600, h=600):
        self.w = w
        self.h = h
        self.display = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption('Snake AI')
        self.clock = pygame.time.Clock()
        self.play_area_w = self.w - (2 * WALL_SIZE)
        self.play_area_h = self.h - (2 * WALL_SIZE) - HUD_HEIGHT
        self.snake_color = BLUE1
        try:
            self.apple_img = pygame.image.load("apple.png").convert_alpha()
            self.apple_img = pygame.transform.scale(self.apple_img, (APPLE_SIZE, APPLE_SIZE))
            self.bg = pygame.image.load("grass.png").convert()
            self.bg = pygame.transform.scale(self.bg, (self.play_area_w, self.play_area_h))
        except:
            self.apple_img = None
            self.bg = None
        self.reset()
    def reset(self):
        self.direction = Direction.RIGHT
        start_x = WALL_SIZE + (self.play_area_w // BLOCK_SIZE // 2) * BLOCK_SIZE
        start_y = HUD_HEIGHT + WALL_SIZE + (self.play_area_h // BLOCK_SIZE // 2) * BLOCK_SIZE
        self.head = Point(start_x, start_y)
        self.snake = [
            self.head,
            Point(self.head.x - BLOCK_SIZE, self.head.y),
            Point(self.head.x - (2 * BLOCK_SIZE), self.head.y)
        ]
        self.score = 0
        self.food = None
        self.frame_iteration = 0
        self._place_food()
    def _place_food(self):
        x = WALL_SIZE + random.randint(0, (self.play_area_w - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
        y = HUD_HEIGHT + WALL_SIZE + random.randint(0, (self.play_area_h - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
        self.food = Point(x, y)
        if self.food in self.snake:
            self._place_food()
    def play_step(self, action):
        self.frame_iteration += 1
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1: self.snake_color = RED
                if event.key == pygame.K_2: self.snake_color = GREEN
                if event.key == pygame.K_3: self.snake_color = YELLOW
                if event.key == pygame.K_4: self.snake_color = PURPLE
                if event.key == pygame.K_0: self.snake_color = BLUE1
        old_dist = np.sqrt((self.head.x - self.food.x) ** 2 + (self.head.y - self.food.y) ** 2)
        self._move(action)
        self.snake.insert(0, self.head)
        reward = 0
        game_over = False
        if self.is_collision() or self.frame_iteration > 100 * len(self.snake):
            return -10, True, self.score
        if self.head == self.food:
            self.score += 1
            reward = 10
            self.frame_iteration = 0
            if eating_sound:
                eating_sound.play()
            self._place_food()
        else:
            self.snake.pop()
            new_dist = np.sqrt((self.head.x - self.food.x) ** 2 + (self.head.y - self.food.y) ** 2)
            reward = 1 if new_dist < old_dist else -1
        self._update_ui()
        self.clock.tick(SPEED)
        return reward, game_over, self.score
    def is_collision(self, pt=None):
        if pt is None:
            pt = self.head
        if pt.x >= self.w - WALL_SIZE or pt.x < WALL_SIZE or \
                pt.y >= self.h - WALL_SIZE or pt.y < HUD_HEIGHT + WALL_SIZE:
            return True
        return pt in self.snake[1:]
    def _update_ui(self):
        self.display.fill(BROWN)
        pygame.draw.rect(self.display, DARK_BROWN, [0, 0, self.w, HUD_HEIGHT])
        self.display.blit(font.render("1-RED, 2-GREEN, 3-YELLOW, 4-PURPLE, 0-ORIGINAL", True, WHITE), [125, 12])
        if self.bg:
            self.display.blit(self.bg, (WALL_SIZE, HUD_HEIGHT + WALL_SIZE))
        else:
            pygame.draw.rect(self.display, (50, 150, 50),
                             [WALL_SIZE, HUD_HEIGHT + WALL_SIZE, self.play_area_w, self.play_area_h])
        for x in range(WALL_SIZE, self.w - WALL_SIZE + 1, BLOCK_SIZE):
            pygame.draw.line(self.display, GRID_COLOR, (x, HUD_HEIGHT + WALL_SIZE), (x, self.h - WALL_SIZE))
        for y in range(HUD_HEIGHT + WALL_SIZE, self.h - WALL_SIZE + 1, BLOCK_SIZE):
            pygame.draw.line(self.display, GRID_COLOR, (WALL_SIZE, y), (self.w - WALL_SIZE, y))
        for i, pt in enumerate(self.snake):
            color = self.snake_color if i % 2 == 0 else WHITE
            pygame.draw.rect(self.display, color, pygame.Rect(pt.x, pt.y, BLOCK_SIZE, BLOCK_SIZE), border_radius=7)
            if i == 0:
                eye_off = 5
                pygame.draw.circle(self.display, WHITE, (pt.x + eye_off, pt.y + eye_off), 4)
                pygame.draw.circle(self.display, WHITE, (pt.x + BLOCK_SIZE - eye_off, pt.y + eye_off), 4)
                pygame.draw.circle(self.display, BLACK, (pt.x + eye_off, pt.y + eye_off), 2)
                pygame.draw.circle(self.display, BLACK, (pt.x + BLOCK_SIZE - eye_off, pt.y + eye_off), 2)
        if self.apple_img:
            self.display.blit(self.apple_img, (self.food.x + (BLOCK_SIZE - APPLE_SIZE) // 2, self.food.y + (BLOCK_SIZE - APPLE_SIZE) // 2))
        else:
            pygame.draw.rect(self.display, (255, 0, 0), [self.food.x, self.food.y, BLOCK_SIZE, BLOCK_SIZE])
        self.display.blit(font.render(f"SCORE: {self.score}", True, WHITE), [20, 12])
        pygame.display.flip()
    def _move(self, action):
        cw = [Direction.RIGHT, Direction.DOWN, Direction.LEFT, Direction.UP]
        idx = cw.index(self.direction)
        if np.array_equal(action, [1, 0, 0]):
            self.direction = cw[idx]
        elif np.array_equal(action, [0, 1, 0]):
            self.direction = cw[(idx + 1) % 4]
        else:
            self.direction = cw[(idx - 1) % 4]
        x = self.head.x
        y = self.head.y
        if self.direction == Direction.RIGHT:
            x += BLOCK_SIZE
        elif self.direction == Direction.LEFT:
            x -= BLOCK_SIZE
        elif self.direction == Direction.DOWN:
            y += BLOCK_SIZE
        elif self.direction == Direction.UP:
            y -= BLOCK_SIZE
        self.head = Point(x, y)