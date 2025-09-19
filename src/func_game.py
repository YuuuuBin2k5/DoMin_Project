import pygame
import random
from config import*
# random vị trí mìn
def toggle_flag(r, c, flags, revealed):
    # Không đặt cờ nếu ô đã mở
    if (r, c) in revealed:
        return
    if (r, c) in flags:
        flags.remove((r, c))
    else:
        flags.add((r, c))

def check_win(board, revealed, Rows, Cols):
    for r in range(Rows):
        for c in range(Cols):
            if board[r][c] != -1 and (r, c) not in revealed:
                return False
    return True

def random_mines_board(Rows, Cols, num_mines, first_click=None, safe_zone=True):
    """
    Sinh board mìn ngẫu nhiên.
    - first_click: tọa độ (r, c) mà người chơi click đầu tiên
    - safe_zone=True: nếu True thì ô đầu tiên và 8 ô lân cận đều không có mìn
    """
    all_cells = [(r, c) for r in range(Rows) for c in range(Cols)]

    # Nếu có click đầu tiên, tạo vùng cấm mìn
    forbidden = set()
    if first_click:
        fr, fc = first_click
        if safe_zone:
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    nr, nc = fr + dr, fc + dc
                    if 0 <= nr < Rows and 0 <= nc < Cols:
                        forbidden.add((nr, nc))
        else:
            forbidden.add((fr, fc))

    # Loại bỏ forbidden khỏi danh sách chọn mìn
    for cell in forbidden:
        if cell in all_cells:
            all_cells.remove(cell)

    # Chọn ngẫu nhiên các mìn
    mines = set(random.sample(all_cells, num_mines))

    # Khởi tạo board 2D
    board = [[0 for _ in range(Cols)] for _ in range(Rows)]
    for (r, c) in mines:
        board[r][c] = -1

    # Tính số mìn xung quanh
    for r in range(Rows):
        for c in range(Cols):
            if board[r][c] == -1:
                continue
            count = 0
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    if dr == 0 and dc == 0:
                        continue
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < Rows and 0 <= nc < Cols and board[nr][nc] == -1:
                        count += 1
            board[r][c] = count

    return board

def reveal_cell(r, c, board, revealed, Rows, Cols):
    if (r, c) in revealed:
        return None

    # Nếu trúng mìn
    if board[r][c] == -1:
        revealed.add((r, c))
        return "mine"

    # BFS queue
    stack = [(r, c)]
    while stack:
        cr, cc = stack.pop()
        if (cr, cc) in revealed:
            continue
        revealed.add((cr, cc))

        # Nếu ô hiện tại = 0 thì mở tiếp lân cận
        if board[cr][cc] == 0:
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    if dr == 0 and dc == 0:
                        continue
                    nr, nc = cr + dr, cc + dc
                    if 0 <= nr < Rows and 0 <= nc < Cols:
                        if (nr, nc) not in revealed and board[nr][nc] != -1:
                            stack.append((nr, nc))

    return "safe"

def reveal_all_mines(board, revealed, Rows, Cols):
    for r in range(Rows):
        for c in range(Cols):
            if board[r][c] == -1:  # nếu là mìn
                revealed.add((r, c))
