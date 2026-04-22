import pygame
import math

def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    # Основной холст для сохранения рисунков
    canvas = pygame.Surface((800, 600))
    clock = pygame.time.Clock()
    
    radius = 2 # Толщина линий
    drawing = False
    mode = "pen"
    color = (255, 255, 255)
    start_pos = (0, 0)
    
    while True:
        pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            
            if event.type == pygame.KEYDOWN:
                # Цвета
                if event.key == pygame.K_r: color = (255, 0, 0)
                if event.key == pygame.K_g: color = (0, 255, 0)
                if event.key == pygame.K_b: color = (0, 0, 255)
                
                # Инструменты
                if event.key == pygame.K_1: mode = "pen"
                if event.key == pygame.K_2: mode = "square"
                if event.key == pygame.K_3: mode = "rect"
                if event.key == pygame.K_4: mode = "circle"
                if event.key == pygame.K_5: mode = "right_triangle"
                if event.key == pygame.K_6: mode = "equilateral_triangle"
                if event.key == pygame.K_7: mode = "rhombus"
                if event.key == pygame.K_0: mode = "eraser"
                
            if event.type == pygame.MOUSEBUTTONDOWN:
                drawing = True
                start_pos = event.pos
                
            if event.type == pygame.MOUSEBUTTONUP:
                # Фиксируем фигуру на холсте при отпускании мыши
                if mode == "square":
                    drawSquare(canvas, color, start_pos, event.pos, radius)
                elif mode == "right_triangle":
                    drawRightTriangle(canvas, color, start_pos, event.pos, radius)
                elif mode == "equilateral_triangle":
                    drawEquilateralTriangle(canvas, color, start_pos, event.pos, radius)
                elif mode == "rhombus":
                    drawRhombus(canvas, color, start_pos, event.pos, radius)
                elif mode == "rect":
                    drawRect(canvas, color, start_pos, event.pos, radius)
                elif mode == "circle":
                    drawCircle(canvas, color, start_pos, event.pos, radius)
                drawing = False
               
                
            if event.type == pygame.MOUSEMOTION and drawing:
                if mode == "pen":
                    drawLineBetween(canvas, event.pos, event.rel, color, radius)
                elif mode == "eraser":
                    drawLineBetween(canvas, event.pos, event.rel, (0, 0, 0), radius * 5)
                        
        screen.blit(canvas, (0, 0))
        
        # Предпросмотр фигуры во время перетаскивания мыши
        if drawing:
            if mode == "square":
                drawSquare(screen, color, start_pos, pos, radius)
            elif mode == "rect":
                drawRect(screen, color, start_pos, pos, radius)
            elif mode == "circle":
                drawCircle(screen, color, start_pos, pos, radius)
            elif mode == "right_triangle":
                drawRightTriangle(screen, color, start_pos, pos, radius)
            elif mode == "equilateral_triangle":
                drawEquilateralTriangle(screen, color, start_pos, pos, radius)
            elif mode == "rhombus":
                drawRhombus(screen, color, start_pos, pos, radius)
                
        pygame.display.flip()
        clock.tick(60)

# --- Функции рисования новых фигур ---

def drawSquare(surface, color, start_pos, end_pos, radius):
    """Рисует квадрат, где сторона определяется разницей по оси X"""
    x1, y1 = start_pos
    x2, y2 = end_pos
    side = abs(x1 - x2) # Вычисляем длину стороны
    # Определяем направление отрисовки
    sign_x = 1 if x2 > x1 else -1
    sign_y = 1 if y2 > y1 else -1
    # Рисуем как прямоугольник с равными сторонами
    pygame.draw.rect(surface, color, (x1, y1, side * sign_x, side * sign_y), radius)

def drawRightTriangle(surface, color, start_pos, end_pos, radius):
    """Рисует прямоугольный треугольник"""
    points = [
        start_pos,                     # Вершина прямого угла
        (start_pos[0], end_pos[1]),    # Нижняя точка
        (end_pos[0], end_pos[1])       # Угол гипотенузы
    ]
    pygame.draw.polygon(surface, color, points, radius)

def drawEquilateralTriangle(surface, color, start_pos, end_pos, radius):
    """Рисует равносторонний треугольник"""
    x1, y1 = start_pos
    x2, y2 = end_pos
    side = abs(x1 - x2)
    height = (math.sqrt(3) / 2) * side # Формула высоты равностороннего треугольника
    
    # Определяем направление (вверх или вниз)
    dir_y = 1 if y2 > y1 else -1
    
    points = [
        (x1, y1),                             # Вершина
        (x1 - side/2, y1 + height * dir_y),   # Левое основание
        (x1 + side/2, y1 + height * dir_y)    # Правое основание
    ]
    pygame.draw.polygon(surface, color, points, radius)

def drawRhombus(surface, color, start_pos, end_pos, radius):
    """Рисует ромб, вписанный в прямоугольник, образованный мышью"""
    x1, y1 = start_pos
    x2, y2 = end_pos
    center_x = (x1 + x2) / 2
    center_y = (y1 + y2) / 2
    
    points = [
        (center_x, y1), # Верхняя точка
        (x2, center_y), # Правая точка
        (center_x, y2), # Нижняя точка
        (x1, center_y)  # Левая точка
    ]
    pygame.draw.polygon(surface, color, points, radius)

def drawLineBetween(surface, pos, rel, color, radius):
    x, y = pos
    last_x, last_y = x - rel[0], y - rel[1]
    dx, dy = x - last_x, y - last_y
    iterations = max(abs(dx), abs(dy))
    for i in range(iterations):
        progress = i / iterations
        pygame.draw.circle(surface, color, (int(last_x + dx * progress), int(last_y + dy * progress)), radius)
        
def drawRect(surface, color, start_pos, end_pos, radius):
    x1, y1 = start_pos
    x2, y2 = end_pos
    width = abs(x1 - x2)
    height = abs(y1 - y2)
    rect_x = min(x1, x2)
    rect_y = min(y1, y2)
    pygame.draw.rect(surface, color, (rect_x, rect_y, width, height), radius)
    
def drawCircle(surface, color, start_pos, end_pos, radius):
    x1, y1 = start_pos
    x2, y2 = end_pos
    r = int(((x1 - x2)**2 + (y1 - y2)**2)**0.5)
    pygame.draw.circle(surface, color, start_pos, r, radius)

if __name__ == "__main__":
    main()