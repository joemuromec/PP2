import pygame
import math
from datetime import datetime

def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    # Основной холст для сохранения рисунков
    canvas = pygame.Surface((800, 600))
    canvas.fill((255, 255, 255))
    clock = pygame.time.Clock()
    
    # Шрифты
    font_ui = pygame.font.SysFont("Arial", 18)
    font_draw = pygame.font.SysFont("Verdana", 24) # Шрифт для рисования на холсте

    radius = 2 # Толщина линий
    drawing = False
    mode = "pen"
    color = (0, 0, 0) # Черный по умолчанию
    start_pos = (0, 0)
    
    # Переменные для текста
    text_buffer = ""
    text_pos = (0, 0)
    is_typing = False

    while True:
        pos = pygame.mouse.get_pos()
        ctrl_held = pygame.key.get_pressed()[pygame.K_LCTRL] or pygame.key.get_pressed()[pygame.K_RCTRL]
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            
            if event.type == pygame.KEYDOWN:
                if is_typing:
                    if event.key == pygame.K_RETURN:
                        # Рендерим текст на постоянный холст
                        txt_surf = font_draw.render(text_buffer, True, color)
                        canvas.blit(txt_surf, text_pos)
                        text_buffer = ""
                        is_typing = False
                    elif event.key == pygame.K_ESCAPE:
                        text_buffer = ""
                        is_typing = False
                    elif event.key == pygame.K_BACKSPACE:
                        text_buffer = text_buffer[:-1]
                    else:
                        # Добавляем символ в буфер (кроме служебных клавиш)
                        if event.unicode:
                            text_buffer += event.unicode
                    continue # Пропускаем остальные проверки, пока печатаем

                # Цвета
                if event.key == pygame.K_r: color = (255, 0, 0)
                if event.key == pygame.K_g: color = (0, 255, 0)
                if event.key == pygame.K_b: color = (0, 0, 255)
                if event.key == pygame.K_k: color = (0, 0, 0)
                if event.key == pygame.K_w: color = (255, 255, 255)

                # Выбор размера кисти
                if event.key == pygame.K_z: radius = 2 # Small
                if event.key == pygame.K_x: radius = 5 # Medium
                if event.key == pygame.K_c: radius = 10 # Large
                
                # Инструменты
                if event.key == pygame.K_1: mode = "pen"
                if event.key == pygame.K_2: mode = "line"
                if event.key == pygame.K_3: mode = "square"
                if event.key == pygame.K_4: mode = "rect"
                if event.key == pygame.K_5: mode = "circle"
                if event.key == pygame.K_6: mode = "right_triangle"
                if event.key == pygame.K_7: mode = "equilateral_triangle"
                if event.key == pygame.K_8: mode = "rhombus"
                if event.key == pygame.K_0: mode = "eraser"
                if event.key == pygame.K_f: mode = "fill"
                if event.key == pygame.K_t: mode = "text"
                
                if event.key == pygame.K_s and ctrl_held:
                    timestamp = datetime.now().strftime(r"%Y%m%d_%H%M%S")
                    filename = f"save_{timestamp}.png"
                    pygame.image.save(canvas, filename)
                    print(f"Canvas saved as {filename}")


            if event.type == pygame.MOUSEBUTTONDOWN:
                if mode == "fill":
                    flood_fill(canvas, event.pos[0], event.pos[1], color)
                elif mode == "text":
                    is_typing = True
                    text_pos = event.pos
                    text_buffer = ""
                else:
                    drawing = True
                    start_pos = event.pos
                
            if event.type == pygame.MOUSEBUTTONUP:
                if drawing:
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
                    elif mode == "line":
                        pygame.draw.line(canvas, color, start_pos, event.pos, radius)
                    drawing = False
               
                
            if event.type == pygame.MOUSEMOTION and drawing:
                if mode == "pen":
                    drawLineBetween(canvas, event.pos, event.rel, color, radius)
                elif mode == "eraser":
                    drawLineBetween(canvas, event.pos, event.rel, (255, 255, 255), radius * 5)
                        
        screen.blit(canvas, (0, 0))
        
        # Предпросмотр фигуры во время перетаскивания мыши
        if drawing:
            if mode == "square":
                drawSquare(screen, color, start_pos, pos, radius)
            elif mode == "line":
                pygame.draw.line(screen, color, start_pos, pos, radius)
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
            
        # Предпросмотр текста в реальном времени
        if is_typing:
            pygame.draw.line(screen, (255, 0, 0), (text_pos[0], text_pos[1]), (text_pos[0], text_pos[1] + 24), 2)
            txt_preview = font_draw.render(text_buffer + "|", True, color)
            screen.blit(txt_preview, text_pos)

        pygame.display.flip()
        clock.tick(60)

# --- Алгоритм заливки (Flood Fill) ---
def flood_fill(surface, x, y, new_color):
    target_color = surface.get_at((x, y))
    if target_color == new_color:
        return
    
    pixels = [(x, y)]
    while pixels:
        cx, cy = pixels.pop()
        if not (0 <= cx < surface.get_width() and 0 <= cy < surface.get_height()):
            continue
        if surface.get_at((cx, cy)) == target_color:
            surface.set_at((cx, cy), new_color)
            pixels.append((cx + 1, cy))
            pixels.append((cx - 1, cy))
            pixels.append((cx, cy + 1))
            pixels.append((cx, cy - 1))

# --- Функции рисования новых фигур ---

def drawSquare(surface, color, start_pos, end_pos, radius):
    x1, y1 = start_pos
    x2, y2 = end_pos

    # Вычисляем размер стороны
    side = abs(x1 - x2)
    
    # Определяем начальную координату X (если ведем влево, вычитаем сторону)
    if x2 > x1:
        rect_x = x1
    else:
        rect_x = x1 - side
        
    # Определяем начальную координату Y (если ведем вверх, вычитаем сторону)
    if y2 > y1:
        rect_y = y1
    else:
        rect_y = y1 - side

    pygame.draw.rect(surface, color, (rect_x, rect_y, side, side), radius)

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
    side = abs(y1 - y2)
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