import pygame
from config import*

def draw_image_board(screen, image, x_Board, y_Board, Rows, Cols, cell_w, cell_h, revealed, board, flags):
    font = pygame.font.SysFont(None, 30)

    for r in range(Rows):
        for c in range(Cols):
            x = x_Board + c * cell_w
            y = y_Board + r * cell_h
            rect_img = pygame.Rect(c * cell_w, r * cell_h, cell_w, cell_h)
            cell_surface = image.subsurface(rect_img)

            if (r, c) in revealed:
                # Ô đã mở
                if board[r][c] == -1:
                    pygame.draw.rect(screen, (200, 0, 0), (x, y, cell_w, cell_h))
                    text = font.render("*", True, (0, 0, 0))
                    screen.blit(text, (x + cell_w // 3, y + cell_h // 4))
                else:
                    pygame.draw.rect(screen, (180, 180, 180), (x, y, cell_w, cell_h))
                    if board[r][c] > 0:
                        text = font.render(str(board[r][c]), True, (0, 0, 0))
                        screen.blit(text, (x + cell_w // 3, y + cell_h // 4))
            else:
                # Ô chưa mở
                screen.blit(cell_surface, (x, y))
                if (r, c) in flags:
                    pygame.draw.rect(screen, (255, 255, 0), (x, y, cell_w, cell_h))  # ô vàng
                    text = font.render("F", True, (0, 0, 0))
                    screen.blit(text, (x + cell_w // 3, y + cell_h // 4))

                pygame.draw.rect(screen, (255, 255, 255), (x, y, cell_w, cell_h), 1)

# --- Hàm vẽ text có viền ---
def render_text_with_outline(text, font, text_color, outline_color, outline_width=1):   
    base = font.render(text, True, text_color)
    size = base.get_size()
    surf = pygame.Surface((size[0]+2*outline_width, size[1]+2*outline_width), pygame.SRCALPHA)

    # Vẽ viền
    for dx in range(-outline_width, outline_width+1):
        for dy in range(-outline_width, outline_width+1):
            if dx != 0 or dy != 0:
                outline_surf = font.render(text, True, outline_color)
                surf.blit(outline_surf, (dx+outline_width, dy+outline_width))

    # Vẽ chữ chính
    surf.blit(base, (outline_width, outline_width))
    return surf
# --- Vẽ button ---
def draw_button(screen, rect, font, color, text=None):
    shadow_rect = rect.move(3, 3)
    pygame.draw.rect(screen, SHADOW_COLOR, shadow_rect, border_radius=8)
    pygame.draw.rect(screen, color, rect, border_radius=8)
    pygame.draw.rect(screen, BLACK, rect, 2, border_radius=8)
    if text:
        text_surf = render_text_with_outline(text, font, TILE_TEXT, BLACK, 1)
        text_rect = text_surf.get_rect(center=rect.center)
        screen.blit(text_surf, text_rect)