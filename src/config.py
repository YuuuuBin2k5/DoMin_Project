import pygame
# 
FPS = 60
WIDTH, HEIGHT = 1100, 640

# Board
x_Board, y_Board = 20, 20
W_Board, H_Board = 600, 600
Rows_Board, Cols_Board = 15, 15
cell_w = W_Board // Cols_Board
cell_h = H_Board // Rows_Board
#
image1 = pygame.image.load("./asset/image/milkyway.jpg")
image1 = pygame.transform.scale(image1, (W_Board, H_Board))

space_bg = pygame.image.load("./asset/image/space_hd.png")
space_bg = pygame.transform.scale(space_bg, (WIDTH, HEIGHT))


# Màu sắc
YELLOW = (246, 255, 0)
BLUE = (148, 224, 255)
DARK_BLUE = (11, 64, 150)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
TILE_TEXT = (255, 255, 255)
EMPTY_COLOR = (13, 27, 71)
SHADOW_COLOR = (180, 180, 180)
WHITE = (255, 255, 255)
