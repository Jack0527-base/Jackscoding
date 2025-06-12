import pygame
import random
import time

# 初始化游戏
pygame.init()

# 颜色定义
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
GRAY = (128, 128, 128)
BUTTON_BLUE = (50, 150, 250)

# 游戏参数
BLOCK_SIZE = 50  # 调大方块尺寸
GRID_WIDTH = 10   # 列数
GRID_HEIGHT = 16  # 行数
GAME_WIDTH = BLOCK_SIZE * GRID_WIDTH
SCREEN_WIDTH = GAME_WIDTH + 200
SCREEN_HEIGHT = BLOCK_SIZE * GRID_HEIGHT

# 初始化屏幕
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("俄罗斯方块 - 修复版")

# 按钮配置
BUTTONS = [
    {"rect": pygame.Rect(GAME_WIDTH+30, 150, 140, 60), "text": "← 左移", "action": "left"},
    {"rect": pygame.Rect(GAME_WIDTH+30, 250, 140, 60), "text": "→ 右移", "action": "right"},
    {"rect": pygame.Rect(GAME_WIDTH+30, 350, 140, 60), "text": "↻ 旋转", "action": "rotate"},
]

# 方块形状定义
SHAPES = [
    [[1, 5, 9, 13], [4, 5, 6, 7]],  # I
    [[4, 5, 9, 10], [2, 6, 5, 9]],  # Z
    [[6, 7, 9, 10], [1, 5, 6, 10]],  # S
    [[1, 2, 5, 9], [0, 4, 5, 6], [1, 5, 9, 8], [4, 5, 6, 10]],  # J
    [[1, 2, 6, 10], [5, 6, 7, 9], [2, 6, 10, 11], [3, 5, 6, 7]],  # L
    [[1, 4, 5, 6], [1, 4, 5, 9], [4, 5, 6, 9], [1, 5, 6, 9]],  # T
    [[1, 2, 5, 6]],  # O
]

COLORS = [CYAN, ORANGE, MAGENTA, YELLOW, (0, 255, 0), (200, 50, 150), (100, 200, 255)]

class Tetris:
    def __init__(self):
        self.grid = [[0] * GRID_WIDTH for _ in range(GRID_HEIGHT)]
        self.score = 0
        self.game_over = False
        self.new_piece()
        self.last_drop = pygame.time.get_ticks()

    def new_piece(self):
        self.shape = random.choice(SHAPES)
        self.color = random.choice(COLORS)
        self.rotation = 0
        self.x = GRID_WIDTH // 2 - 2
        self.y = 0

        if self.check_collision(self.x, self.y, self.rotation):
            self.game_over = True

    def check_collision(self, x, y, rotation):
        shape = self.shape[rotation % len(self.shape)]
        for i in range(4):
            px = x + (shape[i] % 4)
            py = y + (shape[i] // 4)
            if px < 0 or px >= GRID_WIDTH or py >= GRID_HEIGHT:
                return True
            if py >= 0 and self.grid[py][px]:
                return True
        return False

    def rotate(self):
        old_rotation = self.rotation
        self.rotation = (self.rotation + 1) % len(self.shape)
        if self.check_collision(self.x, self.y, self.rotation):
            self.rotation = old_rotation

    def move(self, dx):
        new_x = self.x + dx
        if not self.check_collision(new_x, self.y, self.rotation):
            self.x = new_x

    def drop(self, force=False):
        now = pygame.time.get_ticks()
        if force or (now - self.last_drop) > 800:  # 800ms自动下落
            if not self.check_collision(self.x, self.y + 1, self.rotation):
                self.y += 1
                self.last_drop = now
                return True
            self.lock_piece()
            self.last_drop = now
        return False

    def lock_piece(self):
        shape = self.shape[self.rotation % len(self.shape)]
        for i in range(4):
            px = self.x + (shape[i] % 4)
            py = self.y + (shape[i] // 4)
            if 0 <= py < GRID_HEIGHT and 0 <= px < GRID_WIDTH:
                self.grid[py][px] = self.color
        self.clear_lines()
        self.new_piece()

    def clear_lines(self):
        lines_cleared = 0
        for i in range(GRID_HEIGHT-1, -1, -1):
            if all(self.grid[i]):
                del self.grid[i]
                self.grid.insert(0, [0]*GRID_WIDTH)
                lines_cleared += 1
        self.score += lines_cleared ** 2 * 100

    def draw(self, surface):
        surface.fill(BLACK)
        
        # 绘制当前方块
        shape = self.shape[self.rotation % len(self.shape)]
        for i in range(4):
            px = self.x + (shape[i] % 4)
            py = self.y + (shape[i] // 4)
            if 0 <= py < GRID_HEIGHT and 0 <= px < GRID_WIDTH:
                pygame.draw.rect(surface, self.color, 
                               (px*BLOCK_SIZE, py*BLOCK_SIZE, 
                                BLOCK_SIZE-2, BLOCK_SIZE-2))

        # 绘制固定方块
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if self.grid[y][x]:
                    pygame.draw.rect(surface, self.grid[y][x],
                                   (x*BLOCK_SIZE, y*BLOCK_SIZE,
                                    BLOCK_SIZE-2, BLOCK_SIZE-2))

        # 显示分数
        font = pygame.font.SysFont('simhei', 28)
        text = font.render(f'得分: {self.score}', True, WHITE)
        surface.blit(text, (20, 20))

        if self.game_over:
            font = pygame.font.SysFont('simhei', 48)
            text = font.render('游戏结束', True, RED)
            surface.blit(text, (GAME_WIDTH//2-100, SCREEN_HEIGHT//2-30))

def draw_button(button):
    mouse_pos = pygame.mouse.get_pos()
    color = BUTTON_BLUE if button["rect"].collidepoint(mouse_pos) else GRAY
    pygame.draw.rect(screen, color, button["rect"], border_radius=10)
    pygame.draw.rect(screen, WHITE, button["rect"], 3, border_radius=10)
    
    font = pygame.font.SysFont('simhei', 24)
    text = font.render(button["text"], True, WHITE)
    text_rect = text.get_rect(center=button["rect"].center)
    screen.blit(text, text_rect)

def main():
    game = Tetris()
    clock = pygame.time.Clock()
    game_surface = pygame.Surface((GAME_WIDTH, SCREEN_HEIGHT))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

            # 鼠标控制
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                for button in BUTTONS:
                    if button["rect"].collidepoint(mouse_pos):
                        {
                            "left": lambda: game.move(-1),
                            "right": lambda: game.move(1),
                            "rotate": lambda: game.rotate()
                        }[button["action"]]()

            # 键盘控制
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    game.move(-1)
                elif event.key == pygame.K_RIGHT:
                    game.move(1)
                elif event.key == pygame.K_UP:
                    game.rotate()
                elif event.key == pygame.K_DOWN:
                    game.drop(force=True)

        # 自动下落
        game.drop()

        # 绘制界面
        screen.fill(BLACK)
        
        # 游戏区域
        game.draw(game_surface)
        screen.blit(game_surface, (0, 0))
        
        # 控制面板
        pygame.draw.line(screen, WHITE, (GAME_WIDTH, 0), (GAME_WIDTH, SCREEN_HEIGHT), 4)
        for button in BUTTONS:
            draw_button(button)

        pygame.display.update()
        clock.tick(60)

        if game.game_over:
            time.sleep(2)
            pygame.quit()
            return

if __name__ == "__main__":
    main()