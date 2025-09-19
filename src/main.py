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

#font
font = pygame.font.SysFont(None, 30, bold=True)
#button rect
new_rect = pygame.Rect(700, 50, 100, 50)
player_rect = pygame.Rect(700, 150, 100, 50)
solve_rect = pygame.Rect(700, 250, 100, 50)
back_rect = pygame.Rect(700, 350, 100, 50)
history_rect = pygame.Rect(700, 450, 100, 50)

#
first_click = None
board = None
board_before = None
revealed = set()
flags = set()
is_lose = False
is_win = False
algorithm = "Player"

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
            #button back
            elif back_rect.collidepoint(event.pos):
                if board_before is not None and first_click is not None:
                    board = copy.deepcopy(board_before)
                    revealed = set()
                    flags = set()
                    is_lose = False
                    is_win = False

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
                                print("Game Over!")
                                reveal_all_mines(board, revealed, Rows_Board, Cols_Board)
                                is_lose = True
                    elif event.button == 3:  # chuột phải -> đặt cờ
                        toggle_flag(r, c, flags, revealed)

    if not is_lose and board is not None and check_win(board, revealed, Rows_Board, Cols_Board):
        print("You Win!")
        is_win = True

    screen.fill(DARK_BLUE)
    draw_image_board(screen, image1, x_Board, y_Board, Rows_Board, Cols_Board, cell_w, cell_h, revealed, board, flags)   
      
    draw_button(screen, new_rect, font, DARK_BLUE, "New")
    draw_button(screen, solve_rect, font, DARK_BLUE, "Solver")
    draw_button(screen, history_rect, font, DARK_BLUE, "History")
    draw_button(screen, player_rect, font, DARK_BLUE, algorithm)
    draw_button(screen, back_rect, font, DARK_BLUE, "Back")

    pygame.display.update()
    clock.tick(FPS)