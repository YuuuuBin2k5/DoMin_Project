import copy
import sys
import pygame
from pygame.locals import *
from config import *
from func_game import*
from ui import*

# --- Khởi tạo pygame ---
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Minesweeper")

clock = pygame.time.Clock()

# ================== STARS ==================
# 3 layer sao: xa, trung, gần
stars_far = [[random.randint(0, WIDTH), random.randint(0, HEIGHT)] for _ in range(50)]
stars_mid = [[random.randint(0, WIDTH), random.randint(0, HEIGHT)] for _ in range(40)]
stars_near = [[random.randint(0, WIDTH), random.randint(0, HEIGHT)] for _ in range(30)]

def draw_stars():
    # xa → chậm
    for star in stars_far:
        pygame.draw.circle(screen, (200, 200, 255), (star[0], star[1]), 1)
        star[0] -= 0.3
        if star[0] < 0:
            star[0] = WIDTH
            star[1] = random.randint(0, HEIGHT)
    # trung → vừa
    for star in stars_mid:
        pygame.draw.circle(screen, (230, 230, 255), (star[0], star[1]), 2)
        star[0] -= 0.6
        if star[0] < 0:
            star[0] = WIDTH
            star[1] = random.randint(0, HEIGHT)
    # gần → nhanh
    for star in stars_near:
        pygame.draw.circle(screen, (255, 255, 255), (star[0], star[1]), 3)
        star[0] -= 1
        if star[0] < 0:
            star[0] = WIDTH
            star[1] = random.randint(0, HEIGHT)

# ================== PLANETS ==================
planet_imgs = [
    pygame.image.load("./asset/image/planet1.png").convert_alpha(),
    pygame.image.load("./asset/image/planet2.png").convert_alpha(),
    pygame.image.load("./asset/image/planet3.png").convert_alpha()
]

planets = []

def spawn_planet():
    img = random.choice(planet_imgs)
    size = random.randint(60, 150)
    img = pygame.transform.smoothscale(img, (size, size))
    y = random.randint(50, HEIGHT - 150)
    speed = random.uniform(0.5, 2.0)
    planets.append([WIDTH, y, img, speed])

def draw_planets():
    for planet in planets[:]:
        screen.blit(planet[2], (planet[0], planet[1]))
        planet[0] -= planet[3]
        if planet[0] < -200:
            planets.remove(planet)


#font
font = pygame.font.SysFont(None, 30, bold=True)
#button rect
new_rect = pygame.Rect(700, 50, 100, 50)
player_rect = pygame.Rect(700, 150, 100, 50)
solve_rect = pygame.Rect(700, 250, 100, 50)
back_rect = pygame.Rect(700, 350, 100, 50)
history_rect = pygame.Rect(700, 450, 100, 50)

#
blackhole_effect = None
first_click = None
board = None
board_before = None
revealed = set()
flags = set()
is_lose = False
is_win = False
algorithm = "Player"
# Timer cho hiệu ứng delay
mine_hit_timer = 0
show_all_mines = False


class GameObject:
    def __init__(self, surf, x, y):
        self.surf = surf
        self.pos = [x, y]
    def draw(self, screen):
        rect = self.surf.get_rect(center=self.pos)
        screen.blit(self.surf, rect)


planet_timer = 0
while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            #button new
            if new_rect.collidepoint(event.pos):
                first_click = None
                board = None
                revealed = set()
                flags = set()
                is_lose = False
                is_win = False
                blackhole_effect = None
                mine_hit_timer = 0
                show_all_mines = False
            #button back
            elif back_rect.collidepoint(event.pos):
                if board_before is not None and first_click is not None:
                    board = copy.deepcopy(board_before)
                    revealed = set()
                    flags = set()
                    is_lose = False
                    is_win = False
                    blackhole_effect = None
                    mine_hit_timer = 0
                    show_all_mines = False

                    # mở lại đúng ô đầu tiên
                    r, c = first_click
                    reveal_cell(r, c, board, revealed, Rows_Board, Cols_Board)

            #click cell
            elif algorithm == "Player":
                mx, my = pygame.mouse.get_pos()
                if not is_lose and x_Board <= mx < x_Board + W_Board and y_Board <= my < y_Board + H_Board:
                    c = (mx - x_Board) // cell_w
                    r = (my - y_Board) // cell_h
                    if event.button == 1:  # chuột trái -> mở ô
                        if first_click is None:
                            board = random_mines_board(
                                Rows_Board, Cols_Board, Rows_Board*Cols_Board//6,
                                first_click=(r, c), safe_zone=True
                            )
                            board_before = copy.deepcopy(board)
                            first_click = (r, c)
                        if (r, c) not in flags:  # không mở nếu đã đặt cờ
                            result = reveal_cell(r, c, board, revealed, Rows_Board, Cols_Board)
                            if result == "mine":
                                # Hiện tất cả mìn trước
                                reveal_all_mines(board, revealed, Rows_Board, Cols_Board)
                                is_lose = True
                                show_all_mines = True
                                mine_hit_timer = 0  # Bắt đầu đếm timer

                    elif event.button == 3:  # chuột phải -> đặt cờ
                        toggle_flag(r, c, flags, revealed)
     # --- Clear màn hình trước ---
    screen.blit(space_bg,(0,0))

    # --- Xử lý timer cho hiệu ứng blackhole ---
    if show_all_mines and mine_hit_timer >= 0:
        mine_hit_timer += 1
        # Sau 120 frame (~2 giây) mới tạo hiệu ứng blackhole
        if mine_hit_timer >= 120 and blackhole_effect is None:
            # Tạo danh sách game objects: ô + sao + hành tinh + phi thuyền
            objects = []

            # --- Ô ---
            for r in range(Rows_Board):
                for c in range(Cols_Board):
                    x = x_Board + c*cell_w + cell_w//2
                    y = y_Board + r*cell_h + cell_h//2
                    surf = pygame.Surface((cell_w, cell_h), pygame.SRCALPHA)
                    val = board[r][c]
                    if val == -1:
                        pygame.draw.rect(surf, (50,50,50), (0,0,cell_w,cell_h))
                    elif val > 0:
                        img = number_images.get(val)
                        if img: surf.blit(img, (0,0))
                    else:
                        pygame.draw.rect(surf, (180,180,180), (0,0,cell_w,cell_h))
                    objects.append(GameObject(surf, x, y))

            # --- Sao ---
            for star in stars_far + stars_mid + stars_near:
                surf = pygame.Surface((3,3), pygame.SRCALPHA)
                pygame.draw.circle(surf, (255,255,255), (1,1), 1)
                objects.append(GameObject(surf, star[0], star[1]))

            # --- Hành tinh ---
            for planet in planets:
                objects.append(GameObject(planet[2], planet[0], planet[1]))

            # --- Phi thuyền ---
            spaceship_surf = pygame.image.load("./asset/image/spaceship.png").convert_alpha()
            spaceship_surf = pygame.transform.smoothscale(spaceship_surf, (60,60))
            objects.append(GameObject(spaceship_surf, WIDTH//2, HEIGHT//2 - 150))

            # --- Khởi tạo hiệu ứng hố đen ---
            blackhole_effect = BlackholeEffect(objects, (WIDTH//2, HEIGHT//2))
            show_all_mines = False  # Dừng việc hiển thị tất cả mìn

    # --- Vẽ background ---
    draw_stars()
    planet_timer += 1
    if planet_timer > 180:  # ~3 giây spawn 1 hành tinh
        spawn_planet()
        planet_timer = 0
    draw_planets()

    # --- Kiểm tra thắng thua ---
    if not is_lose and board is not None and check_win(board, revealed, Rows_Board, Cols_Board):
        print("You Win!")
        is_win = True

    if not blackhole_effect:
        draw_image_board(screen, image1, x_Board, y_Board, Rows_Board, Cols_Board, cell_w, cell_h, revealed, board, flags)
  
   # Vẽ hiệu ứng hố đen nếu thua
   # Vẽ hố đen
    if blackhole_effect:
        blackhole_effect.update()
        blackhole_effect.draw(screen)

    # Vẽ nút luôn trên cùng
    # Vẽ nút
    draw_button(screen, new_rect, font, DARK_BLUE, "New" if not blackhole_effect else "PLAY AGAIN?")
    draw_button(screen, solve_rect, font, DARK_BLUE, "Solver")
    draw_button(screen, history_rect, font, DARK_BLUE, "History")
    draw_button(screen, player_rect, font, DARK_BLUE, algorithm)
    draw_button(screen, back_rect, font, DARK_BLUE, "Back")

    pygame.display.update()
    clock.tick(FPS)