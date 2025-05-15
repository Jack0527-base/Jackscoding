import pygame
import math
import numpy as np

# 初始化pygame
pygame.init()
WIDTH, HEIGHT = 1200, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
FPS = 60

# 颜色定义
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
GRAY = (200, 200, 200)

# 物理常数
k = 8.988e3  # 库仑常数（简化值）

class Charge:
    def __init__(self, x, y, q=1):
        self.x = x
        self.y = y
        self.q = q
        self.radius = 15
        self.dragging = False

    @property
    def pos(self):
        return np.array([self.x, self.y])

    def draw(self, surface):
        color = RED if self.q > 0 else BLUE
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), self.radius)
        font = pygame.font.SysFont(None, 24)
        text = font.render(f"{abs(self.q):.1f}", True, WHITE)
        surface.blit(text, (self.x-10, self.y-10))

class ElectricField:
    def __init__(self):
        self.charges = []
        self.grid_size = 20
        self.selected_charge = None

    def add_charge(self, charge):
        self.charges.append(charge)

    def calculate_field(self, pos):
        total_field = np.array([0.0, 0.0])
        for charge in self.charges:
            r_vec = pos - charge.pos
            r = np.linalg.norm(r_vec)
            if r < 1e-6:
                return np.array([0, 0])
            e_mag = k * abs(charge.q) / r*r    
            e_vec = e_mag * r_vec / r
            if charge.q < 0:
                e_vec *= -1
            total_field += e_vec
        return total_field

    def draw_field(self, surface):
        for x in range(0, WIDTH, self.grid_size):
            for y in range(0, HEIGHT, self.grid_size):
                field = self.calculate_field(np.array([x, y]))
                magnitude = np.linalg.norm(field)
                if magnitude > 0:
                    angle = math.atan2(field[1], field[0])
                    length = min(30, magnitude)
                    
                    # 绘制箭头
                    end = (x + length * math.cos(angle), 
                          y + length * math.sin(angle))
                    pygame.draw.line(surface, BLACK, (x, y), end, 2)
                    
                    # 箭头头部
                    arrow_size = 5
                    left = (end[0] + arrow_size * math.cos(angle + 2.5),
                           end[1] + arrow_size * math.sin(angle + 2.5))
                    right = (end[0] + arrow_size * math.cos(angle - 2.5),
                            end[1] + arrow_size * math.sin(angle - 2.5))
                    pygame.draw.polygon(surface, BLACK, [end, left, right])

class Button:
    def __init__(self, x, y, width, height, color, text, callback):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.text = text
        self.callback = callback
        self.hovered = False

    def draw(self, surface):
        bg_color = (min(self.color[0]+50, 255), 
                   min(self.color[1]+50, 255), 
                   min(self.color[2]+50, 255)) if self.hovered else self.color
        pygame.draw.rect(surface, bg_color, self.rect)
        font = pygame.font.SysFont(None, 28)
        text_surf = font.render(self.text, True, BLACK)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def check_hover(self, pos):
        self.hovered = self.rect.collidepoint(pos)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.hovered:
            self.callback()

def main():
    running = True
    field = ElectricField()
    
    # 初始化电荷
    field.add_charge(Charge(300, 300, 5))
    field.add_charge(Charge(500, 300, -5))

    # 按钮回调函数
    def increase_charge():
        if field.selected_charge:
            field.selected_charge.q += 1
            field.selected_charge.q = min(10, field.selected_charge.q)

    def decrease_charge():
        if field.selected_charge:
            field.selected_charge.q -= 1
            field.selected_charge.q = max(-10, field.selected_charge.q)

    # 创建按钮
    buttons = [
        Button(WIDTH-120, 10, 50, 40, GRAY, "+", increase_charge),
        Button(WIDTH-60, 10, 50, 40, GRAY, "-", decrease_charge)
    ]

    while running:
        screen.fill(WHITE)
        
        # 事件处理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # 处理按钮事件
            mouse_pos = pygame.mouse.get_pos()
            for button in buttons:
                button.check_hover(mouse_pos)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    button.handle_event(event)

            # 电荷拖动事件
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                for charge in field.charges:
                    if np.linalg.norm(np.array(pos) - charge.pos) < charge.radius:
                        charge.dragging = True
                        field.selected_charge = charge
                        break
            
            if event.type == pygame.MOUSEBUTTONUP:
                for charge in field.charges:
                    charge.dragging = False
                field.selected_charge = None
            
            if event.type == pygame.MOUSEMOTION:
                for charge in field.charges:
                    if charge.dragging:
                        charge.x, charge.y = pygame.mouse.get_pos()
            
            if event.type == pygame.MOUSEWHEEL:
                if field.selected_charge:
                    field.selected_charge.q += event.y * 0.5
                    field.selected_charge.q = max(-10, min(10, field.selected_charge.q))

        # 绘制电场
        field.draw_field(screen)
        
        # 绘制电荷
        for charge in field.charges:
            charge.draw(screen)
        
        # 绘制按钮
        for button in buttons:
            button.draw(screen)
        
        # 绘制提示信息
        font = pygame.font.SysFont(None, 24)
        text = font.render("SUAN is the BEST", True, RED)
        screen.blit(text, (10, 10))
        
        # 显示选中电荷电量
        if field.selected_charge:
            q_text = font.render(f"Selected Charge: {field.selected_charge.q:.1f}", True, BLACK)
            screen.blit(q_text, (WIDTH-250, HEIGHT-40))
        
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()