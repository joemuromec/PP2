import pygame

def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    # Canvas for drawing
    canvas = pygame.Surface((800, 600))
    clock = pygame.time.Clock()
    
    radius = 15
    drawing = False
    mode = "pen"
    color = (0, 0, 255)
    
    start_pos = (0, 0)
    
    while True:
        pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN:
                # Color selection
                if event.key == pygame.K_r: color = (255, 0, 0)
                if event.key == pygame.K_g: color = (0, 255, 0)
                if event.key == pygame.K_b: color = (0, 0, 255)
                
                # Tools selection
                if event.key == pygame.K_p: mode = "pen"
                if event.key == pygame.K_s: mode = "rect"
                if event.key == pygame.K_c: mode = "circle"
                if event.key == pygame.K_e: mode = "eraser"
                
            if event.type == pygame.MOUSEBUTTONDOWN:
                drawing = True
                start_pos = event.pos
                
            if event.type == pygame.MOUSEBUTTONUP:
                if mode == "rect":
                    drawRect(canvas, color, start_pos, event.pos, radius)
                elif mode == "circle":
                    drawCircle(canvas, color, start_pos, event.pos, radius)
                drawing = False
                
            if event.type == pygame.MOUSEMOTION:
                if drawing:
                    if mode == "pen":
                        drawLineBetween(canvas, event.pos, event.rel, color, radius)
                    elif mode == "eraser":
                        drawLineBetween(canvas, event.pos, event.rel, (0, 0, 0), radius)
                        
                
        screen.blit(canvas, (0, 0))
        
        if drawing:
            if mode == "rect":
                drawRect(screen, color, start_pos, pos, radius)
            if mode == "circle":
                drawCircle(screen, color, start_pos, pos, radius)
                
                
        pygame.display.flip()
        clock.tick(60)

def drawLineBetween(surface, pos, rel, color, radius):
    x, y = pos
    last_x, last_y = x - rel[0], y - rel[1]
    
    dx = x - last_x
    dy = y - last_y
    
    iterations = max(abs(dx), abs(dy))
    
    for i in range(iterations):
        progress = i / iterations
        draw_x = int(last_x + dx * progress)
        draw_y = int(last_y + dy * progress)
        pygame.draw.circle(surface, color, (draw_x, draw_y), radius)
        
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

main()