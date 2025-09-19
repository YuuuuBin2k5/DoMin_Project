import math
import os
import random
import pygame
from config import *

# --- Load ảnh số 1-8 ---
number_images = {
    n: pygame.image.load(f"./asset/image/number/{n}.jpg")
    for n in range(1, 9)
}
for n in number_images:
    number_images[n] = pygame.transform.smoothscale(number_images[n], (cell_w, cell_h))

# --- Load frames hố đen ---
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
frames_dir = os.path.join(BASE_DIR, "asset", "image", "frames")

blackhole_frames = []

if os.path.exists(frames_dir):
    for filename in sorted(os.listdir(frames_dir)):
        if filename.endswith(".png") and filename.startswith("frame_"):
            try:
                img = pygame.image.load(os.path.join(frames_dir, filename))
                img = pygame.transform.smoothscale(img, (cell_w, cell_h))
                blackhole_frames.append(img)
            except Exception as e:
                print(f"⚠️ Failed to load {filename}: {e}")
else:
    print(f"⚠️ Frames folder not found: {frames_dir}")

frame_index = 0

# --- Hiệu ứng blackhole phóng to ---
class BlackholeEffect:
    def __init__(self, game_objects, center):
        self.objects = game_objects
        self.x, self.y = center
        self.radius = 0
        self.radius_speed = 10  # tốc độ hố đen to lên
        self.active = True

    def update(self):
        if not self.active:
            return
        self.radius += self.radius_speed

        for obj in self.objects:
            dx = self.x - obj.pos[0]
            dy = self.y - obj.pos[1]
            distance = (dx**2 + dy**2)**0.5 + 0.001
            angle = math.atan2(dy, dx) + random.uniform(-0.05, 0.05)
            speed = min(20, distance*0.3)
            obj.pos[0] += math.cos(angle)*speed
            obj.pos[1] += math.sin(angle)*speed

        max_dist = max(((obj.pos[0]-self.x)**2 + (obj.pos[1]-self.y)**2)**0.5 for obj in self.objects)
        if max_dist < 15:
            self.active = False

    def draw(self, screen):
        for obj in self.objects:
            obj.draw(screen)
        # hố đen lớn
        # trong BlackholeEffect.draw()
        alpha = min(100, int(self.radius*0.5))  # càng to càng đậm, max alpha 200
        bh_surf = pygame.Surface((self.radius*2, self.radius*2), pygame.SRCALPHA)
        pygame.draw.circle(bh_surf, (0,0,0,alpha), (self.radius,self.radius), self.radius)
        rect = bh_surf.get_rect(center=(self.x, self.y))
        screen.blit(bh_surf, rect)




def create_blackhole_surface(radius):
    surf = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
    for r in range(radius, 0, -1):
        alpha = int(255 * (r / radius))
        pygame.draw.circle(surf, (0,0,0,alpha), (radius,radius), r)
    return surf


# --- Vẽ hố đen bình thường (không hiệu ứng) ---
def draw_blackhole(screen, x, y):
    global frame_index
    if blackhole_frames:
        frame = blackhole_frames[frame_index // 5 % len(blackhole_frames)]
        rect = frame.get_rect(center=(x, y))
        screen.blit(frame, rect)
        frame_index = (frame_index + 1) % (len(blackhole_frames) * 5)
    else:
        pygame.draw.circle(screen, (0, 0, 0), (x, y), 15)

# --- Vẽ board ---
def draw_image_board(screen, image, x_Board, y_Board, Rows, Cols, cell_w, cell_h, revealed, board, flags, effects=[]):
    font = pygame.font.SysFont(None, 30)

    for r in range(Rows):
        for c in range(Cols):
            x = x_Board + c * cell_w
            y = y_Board + r * cell_h
            rect_img = pygame.Rect(c * cell_w, r * cell_h, cell_w, cell_h)
            cell_surface = image.subsurface(rect_img)

            if (r, c) in revealed:
                if board[r][c] == -1:
                    # Vẽ hố đen hoặc hiệu ứng nếu có
                    active_effect = None
                    for effect in effects:
                        if effect.x == x + cell_w//2 and effect.y == y + cell_h//2 and effect.active:
                            active_effect = effect
                            break
                    if active_effect:
                        active_effect.draw(screen)
                    else:
                        draw_blackhole(screen, x + cell_w//2, y + cell_h//2)
                else:
                    pygame.draw.rect(screen, (180, 180, 180), (x, y, cell_w, cell_h))
                    if board[r][c] > 0:
                        img = number_images.get(board[r][c])
                        if img:
                            screen.blit(img, (x, y))
                        else:
                            text = font.render(str(board[r][c]), True, (0,0,0))
                            screen.blit(text, (x + cell_w // 3, y + cell_h // 4))
            else:
                if (r, c) in flags:
                    pygame.draw.rect(screen, (255, 255, 0, 180), (x, y, cell_w, cell_h))
                    text = font.render("F", True, (0,0,0))
                    screen.blit(text, (x + cell_w // 3, y + cell_h // 4))
                pygame.draw.rect(screen, (255,255,255), (x, y, cell_w, cell_h), 1)

# --- Vẽ text có viền ---
def render_text_with_outline(text, font, text_color, outline_color, outline_width=1):
    base = font.render(text, True, text_color)
    size = base.get_size()
    surf = pygame.Surface((size[0]+2*outline_width, size[1]+2*outline_width), pygame.SRCALPHA)

    for dx in range(-outline_width, outline_width+1):
        for dy in range(-outline_width, outline_width+1):
            if dx !=0 or dy !=0:
                outline_surf = font.render(text, True, outline_color)
                surf.blit(outline_surf, (dx+outline_width, dy+outline_width))
    surf.blit(base, (outline_width, outline_width))
    return surf

# --- Vẽ button ---
def draw_button(screen, rect, font, color, text=None):
    shadow_rect = rect.move(3,3)
    pygame.draw.rect(screen, SHADOW_COLOR, shadow_rect, border_radius=8)
    pygame.draw.rect(screen, color, rect, border_radius=8)
    pygame.draw.rect(screen, BLACK, rect, 2, border_radius=8)
    if text:
        text_surf = render_text_with_outline(text, font, TILE_TEXT, BLACK, 1)
        text_rect = text_surf.get_rect(center=rect.center)
        screen.blit(text_surf, text_rect)
