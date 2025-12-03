# main.py
import pygame
import random
import os
import sys
import math

# 导入核心定义和 AI 模块
from tetris_core import *
import ai

# 初始化
pygame.init()
pygame.font.init()
pygame.mixer.init()
pygame.key.set_repeat(200, 50)

# --- 声音加载 ---
SOUND_LOADED = False
try:
    if os.path.exists('bgm.mp3'):
        pygame.mixer.music.load('bgm.mp3')
        pygame.mixer.music.set_volume(0.4)
    if os.path.exists('clear.wav'):
        CLEAR_SOUND = pygame.mixer.Sound('clear.wav')
        CLEAR_SOUND.set_volume(0.6)
        SOUND_LOADED = True
    else:
        CLEAR_SOUND = None
    if os.path.exists('fall.wav'):
        FALL_SOUND = pygame.mixer.Sound('fall.wav')
        FALL_SOUND.set_volume(0.5)
    else:
        FALL_SOUND = None
except Exception as e:
    print(f"Sound Error: {e}")

# ==========================================
# --- 粒子系统 ---
# ==========================================
class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        angle = random.uniform(0, 6.28) 
        speed = random.uniform(3, 8)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed - 3
        self.gravity = 0.8
        self.life = 255 
        self.decay = random.randint(5, 12)
        self.size = random.randint(6, 12)
        self.rotation = random.randint(0, 360) 
        self.rot_speed = random.uniform(-15, 15)

    def update(self):
        self.vy += self.gravity
        self.x += self.vx
        self.y += self.vy
        self.rotation += self.rot_speed
        self.life -= self.decay
        if self.size > 0.1:
            self.size -= 0.3 

    def draw(self, surface):
        if self.life > 0:
            s = pygame.Surface((int(self.size), int(self.size)), pygame.SRCALPHA)
            r, g, b = self.color
            s.fill((r, g, b, max(0, int(self.life))))
            rotated_s = pygame.transform.rotate(s, self.rotation)
            surface.blit(rotated_s, (int(self.x) - rotated_s.get_width()//2, int(self.y) - rotated_s.get_height()//2))

def generate_explosion_particles(full_rows, grid):
    new_particles = []
    for r in full_rows:
        for c in range(10):
            color = grid[r][c]
            if color != (0,0,0):
                for _ in range(8):
                    start_x = TOP_LEFT_X + c * BLOCK_SIZE + BLOCK_SIZE / 2
                    start_y = TOP_LEFT_Y + r * BLOCK_SIZE + BLOCK_SIZE / 2
                    new_particles.append(Particle(start_x, start_y, color))
    return new_particles

# ==========================================
# --- 绘制函数 ---
# ==========================================
def draw_text_middle(surface, text, size, color):
    font = pygame.font.SysFont("arial", size, bold=True)
    label = font.render(text, 1, color)
    surface.blit(label, (TOP_LEFT_X + PLAY_WIDTH/2 - (label.get_width()/2), 
                         TOP_LEFT_Y + PLAY_HEIGHT/2 - label.get_height()/2))

def draw_grid(surface, grid):
    sx = TOP_LEFT_X
    sy = TOP_LEFT_Y
    for i in range(len(grid)):
        pygame.draw.line(surface, GRID_COLOR, (sx, sy + i*BLOCK_SIZE), (sx+PLAY_WIDTH, sy+ i*BLOCK_SIZE))
        for j in range(len(grid[i])):
            pygame.draw.line(surface, GRID_COLOR, (sx + j*BLOCK_SIZE, sy), (sx + j*BLOCK_SIZE, sy + PLAY_HEIGHT))

def draw_next_shape(shape, surface):
    font = pygame.font.SysFont('comicsans', 30)
    label = font.render('Next Shape', 1, (255,255,255))
    sx = TOP_LEFT_X + PLAY_WIDTH + 50
    sy = TOP_LEFT_Y + PLAY_HEIGHT/2 - 100
    format = shape.shape[shape.rotation % len(shape.shape)]
    for i, line in enumerate(format):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                rect_x = sx + j*BLOCK_SIZE
                rect_y = sy + i*BLOCK_SIZE
                pygame.draw.rect(surface, shape.color, (rect_x, rect_y, BLOCK_SIZE, BLOCK_SIZE), 0)
                pygame.draw.rect(surface, (0,0,0), (rect_x, rect_y, BLOCK_SIZE, BLOCK_SIZE), 1)
    surface.blit(label, (sx + 10, sy - 30))

def draw_window(surface, grid, score=0, last_score=0, current_piece=None):
    surface.fill(BG_COLOR)
    font = pygame.font.SysFont('comicsans', 60)
    label = font.render('Tetris', 1, (255, 255, 255))
    surface.blit(label, (TOP_LEFT_X + PLAY_WIDTH / 2 - (label.get_width() / 2), 30))
    
    font_small = pygame.font.SysFont('comicsans', 30)
    sx = TOP_LEFT_X + PLAY_WIDTH + 50
    sy = TOP_LEFT_Y + PLAY_HEIGHT/2 - 100
    label_score = font_small.render('Score: ' + str(score), 1, (255,255,255))
    surface.blit(label_score, (sx + 20, sy + 160))
    label_high = font_small.render('High Score: ' + str(last_score), 1, (255,255,255))
    surface.blit(label_high, (sx + 20, sy + 200))
    
    font_hint = pygame.font.SysFont('arial', 20)
    label_pause = font_hint.render('Press ESC to Pause', 1, (255, 200, 0))
    label_ai = font_hint.render('Press A for AI Agent', 1, (0, 255, 255))
    label_space = font_hint.render('Space for Hard Drop', 1, (200, 200, 200))
    surface.blit(label_pause, (sx + 20, sy + 260))
    surface.blit(label_ai, (sx + 20, sy + 290))
    surface.blit(label_space, (sx + 20, sy + 320))

    for i in range(len(grid)):
        for j in range(len(grid[i])):
            rect_x = TOP_LEFT_X + j*BLOCK_SIZE
            rect_y = TOP_LEFT_Y + i*BLOCK_SIZE
            pygame.draw.rect(surface, grid[i][j], (rect_x, rect_y, BLOCK_SIZE, BLOCK_SIZE), 0)
            if grid[i][j] != (0,0,0):
                 pygame.draw.rect(surface, (0,0,0), (rect_x, rect_y, BLOCK_SIZE, BLOCK_SIZE), 1)

    draw_grid(surface, grid)
    
    if current_piece:
        ghost = Piece(current_piece.x, current_piece.y, current_piece.shape)
        ghost.rotation = current_piece.rotation
        while valid_space(ghost, grid):
            ghost.y += 1
        ghost.y -= 1
        formatted = convert_shape_format(ghost)
        for pos in formatted:
            x, y = pos
            if y > -1:
                rect_x = TOP_LEFT_X + x * BLOCK_SIZE
                rect_y = TOP_LEFT_Y + y * BLOCK_SIZE
                s = pygame.Surface((BLOCK_SIZE, BLOCK_SIZE))
                s.set_alpha(60)
                s.fill(current_piece.color)
                surface.blit(s, (rect_x, rect_y))
                pygame.draw.rect(surface, (200,200,200), (rect_x, rect_y, BLOCK_SIZE, BLOCK_SIZE), 1)

    if current_piece:
        formatted = convert_shape_format(current_piece)
        for pos in formatted:
            x, y = pos
            if y > -1:
                rect_x = TOP_LEFT_X + x * BLOCK_SIZE
                rect_y = TOP_LEFT_Y + y * BLOCK_SIZE
                pygame.draw.rect(surface, current_piece.color, (rect_x, rect_y, BLOCK_SIZE, BLOCK_SIZE), 0)
                pygame.draw.rect(surface, (0,0,0), (rect_x, rect_y, BLOCK_SIZE, BLOCK_SIZE), 1)

    pygame.draw.rect(surface, BORDER_COLOR, (TOP_LEFT_X, TOP_LEFT_Y, PLAY_WIDTH, PLAY_HEIGHT), 4)

def draw_responsive(fake_screen, win):
    game_w, game_h = fake_screen.get_size()
    win_w, win_h = win.get_size()
    scale = min(win_w / game_w, win_h / game_h)
    new_w = int(game_w * scale)
    new_h = int(game_h * scale)
    offset_x = (win_w - new_w) // 2
    offset_y = (win_h - new_h) // 2
    win.fill((0, 0, 0))
    scaled_surface = pygame.transform.scale(fake_screen, (new_w, new_h))
    win.blit(scaled_surface, (offset_x, offset_y))

def get_fall_speed(level):
    return max(0.05, 0.5 - (level - 1) * 0.05)

def update_score(nscore):
    score = max_score()
    with open('scores.txt', 'w') as f:
        if int(score) > nscore: f.write(str(score))
        else: f.write(str(nscore))

def max_score():
    if not os.path.exists('scores.txt'): return 0
    try:
        with open('scores.txt', 'r') as f:
            lines = f.readlines()
            score = lines[0].strip()
    except: score = 0
    return score

# ==========================================
# --- 主游戏循环 ---
# ==========================================
def main(win, level):
    last_score = max_score()
    locked_positions = {}
    grid = create_grid(locked_positions)
    change_piece = False
    run = True
    paused = False 
    ai_mode = False
    ai_timer = 0
    current_target = None
    
    current_piece = get_shape()
    next_piece = get_shape()
    clock = pygame.time.Clock()
    fall_time = 0
    fall_speed = get_fall_speed(level)
    score = 0
    last_pause_time = 0 
    
    particles = []
    fake_screen = pygame.Surface((S_WIDTH, S_HEIGHT))

    if pygame.mixer.get_init() and not pygame.mixer.music.get_busy():
         try: pygame.mixer.music.play(-1)
         except: pass

    while run:
        grid = create_grid(locked_positions)
        current_time = pygame.time.get_ticks()
        
        if not paused:
            fall_time += clock.get_rawtime()
            if ai_mode: ai_timer += clock.get_rawtime()
        clock.tick()

        if not paused:
            if fall_time/1000 > fall_speed:
                fall_time = 0
                current_piece.y += 1
                if not valid_space(current_piece, grid) and current_piece.y > 0:
                    current_piece.y -= 1
                    change_piece = True

        if ai_mode and not paused and not change_piece:
            if current_target is None:
                current_target = ai.get_best_move(grid, current_piece, next_piece)
            
            if ai_timer > 20: 
                ai_timer = 0
                target_x, target_r = current_target
                if current_piece.rotation % len(current_piece.shape) != target_r:
                    current_piece.rotation += 1
                    if not valid_space(current_piece, grid): current_piece.rotation -= 1
                elif current_piece.x < target_x:
                    current_piece.x += 1
                    if not valid_space(current_piece, grid): current_piece.x -= 1
                elif current_piece.x > target_x:
                    current_piece.x -= 1
                    if not valid_space(current_piece, grid): current_piece.x += 1
                else:
                    while valid_space(current_piece, grid): current_piece.y += 1
                    current_piece.y -= 1
                    change_piece = True
                    current_target = None

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.display.quit()
                pygame.quit()
                sys.exit() 
            if event.type == pygame.VIDEORESIZE:
                win = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if current_time - last_pause_time > 300:
                        paused = not paused
                        last_pause_time = current_time
                        if pygame.mixer.get_init():
                            if paused: pygame.mixer.music.pause()
                            else: pygame.mixer.music.unpause()
                if event.key == pygame.K_a:
                    ai_mode = not ai_mode
                    current_target = None
                
                if not paused and not ai_mode:
                    if event.key == pygame.K_LEFT:
                        current_piece.x -= 1
                        if not valid_space(current_piece, grid): current_piece.x += 1
                    elif event.key == pygame.K_RIGHT:
                        current_piece.x += 1
                        if not valid_space(current_piece, grid): current_piece.x -= 1
                    elif event.key == pygame.K_DOWN:
                        current_piece.y += 1
                        if not valid_space(current_piece, grid): current_piece.y -= 1
                    elif event.key == pygame.K_UP:
                        old_rotation = current_piece.rotation
                        current_piece.rotation += 1
                        if not valid_space(current_piece, grid):
                            current_piece.x += 1
                            if not valid_space(current_piece, grid):
                                current_piece.x -= 2
                                if not valid_space(current_piece, grid):
                                    current_piece.x += 3
                                    if not valid_space(current_piece, grid):
                                         current_piece.x -= 4
                                         if not valid_space(current_piece, grid):
                                             current_piece.x += 2
                                             current_piece.rotation = old_rotation
                    elif event.key == pygame.K_SPACE:
                        while valid_space(current_piece, grid): current_piece.y += 1
                        current_piece.y -= 1
                        change_piece = True

        if change_piece:
            if FALL_SOUND: FALL_SOUND.play()
            shape_pos = convert_shape_format(current_piece)
            for pos in shape_pos:
                p = (pos[0], pos[1])
                locked_positions[p] = current_piece.color
            
            # --- 判断消除前，强制更新网格数据 ---
            # 这样 clear_rows 才能看到刚刚落下的方块
            grid = create_grid(locked_positions)

            # 检查满行以生成粒子
            full_rows = []
            for i in range(len(grid)-1, -1, -1):
                if (0,0,0) not in grid[i]:
                    full_rows.append(i)
            
            if full_rows:
                if CLEAR_SOUND: CLEAR_SOUND.play()
                particles.extend(generate_explosion_particles(full_rows, grid))
            
            current_piece = next_piece
            next_piece = get_shape()
            change_piece = False
            current_target = None
            
            # --- 调用消除函数 ---
            cleared_rows = clear_rows(grid, locked_positions)
            if cleared_rows > 0:
                base_points = {1: 40, 2: 100, 3: 300, 4: 1200}
                score += base_points.get(cleared_rows, 0) * level

        draw_window(fake_screen, grid, score, last_score, current_piece)
        
        alive_particles = []
        for p in particles:
            p.update()
            p.draw(fake_screen)
            if p.life > 0:
                alive_particles.append(p)
        particles = alive_particles 
        
        # 熔断机制，防止粒子过多影响性能表现
        if len(particles) > 250:
            particles = particles[-250:]
        
        draw_next_shape(next_piece, fake_screen)

        if paused:
            overlay = pygame.Surface((S_WIDTH, S_HEIGHT))
            overlay.set_alpha(150)
            overlay.fill((0,0,0))
            fake_screen.blit(overlay, (0,0))
            font_list = pygame.font.get_fonts()
            font_name = 'arial' if 'arial' in font_list else None 
            pause_font = pygame.font.SysFont(font_name, 100, bold=True)
            label = pause_font.render("PAUSED", 1, (255, 255, 255))
            fake_screen.blit(label, (S_WIDTH/2 - label.get_width()/2, S_HEIGHT/2 - label.get_height()/2))
        
        if ai_mode and not paused:
            font_ai = pygame.font.SysFont('comicsans', 40)
            label_ai = font_ai.render("AI AUTO-PILOT", 1, (0, 255, 255))
            fake_screen.blit(label_ai, (S_WIDTH/2 - label_ai.get_width()/2, 20))

        draw_responsive(fake_screen, win)
        pygame.display.update()

        if check_lost(locked_positions):
            draw_text_middle(fake_screen, "YOU LOST!", 80, (255,255,255))
            draw_responsive(fake_screen, win)
            pygame.display.update()
            pygame.time.delay(1500)
            run = False
            update_score(score)
            if pygame.mixer.get_init(): pygame.mixer.music.stop()

# --- 菜单 ---
def main_menu(win):
    run = True
    level = 1
    title_font = pygame.font.SysFont('comicsans', 80, bold=True)
    menu_font = pygame.font.SysFont('comicsans', 50)
    info_font = pygame.font.SysFont('arial', 20)
    fake_screen = pygame.Surface((S_WIDTH, S_HEIGHT))

    while run:
        fake_screen.fill(BG_COLOR)
        title_text = "TETRIS"
        title_shadow = title_font.render(title_text, 1, (0, 0, 0))
        fake_screen.blit(title_shadow, (S_WIDTH/2 - title_shadow.get_width()/2 + 4, 104))
        title_main = title_font.render(title_text, 1, (255, 215, 0))
        fake_screen.blit(title_main, (S_WIDTH/2 - title_main.get_width()/2, 100))
        pygame.draw.line(fake_screen, (255, 215, 0), (S_WIDTH/2 - 150, 190), (S_WIDTH/2 + 150, 190), 3)
        start_label = menu_font.render("Press ENTER to Start", 1, (255, 255, 255))
        fake_screen.blit(start_label, (S_WIDTH/2 - start_label.get_width()/2, 300))
        level_label = menu_font.render(f"< Level: {level} >", 1, (0, 255, 0) if level < 6 else (255, 100, 0))
        fake_screen.blit(level_label, (S_WIDTH/2 - level_label.get_width()/2, 380))
        credits_text = info_font.render("Arrows to Move | ESC to Pause | A for AI", 1, (150, 150, 180))
        fake_screen.blit(credits_text, (S_WIDTH/2 - credits_text.get_width()/2, S_HEIGHT - 50))

        for event in pygame.event.get():
            if event.type == pygame.QUIT: run = False
            if event.type == pygame.VIDEORESIZE:
                win = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN: main(win, level)
                if event.key == pygame.K_UP or event.key == pygame.K_RIGHT:
                    if level < 10: level += 1
                if event.key == pygame.K_DOWN or event.key == pygame.K_LEFT:
                    if level > 1: level -= 1
        
        draw_responsive(fake_screen, win)
        pygame.display.update()
    
    # --- 使用标准的系统退出命令 ---
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    win = pygame.display.set_mode((S_WIDTH, S_HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption('Tetris AI Ultimate')
    main_menu(win)