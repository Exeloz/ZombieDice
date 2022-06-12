from numpy import number
import pygame
from pygame.locals import *
import math

class Grid:
    def __init__(self, screen, size, number_cells) -> None:
        self.screen = screen
        self.width, self.height = size
        self.number_h_cells, self.number_v_cells = number_cells
        self.epsilon = 2

        self.cell_width = math.ceil(self.width/self.number_h_cells)
        self.cell_height = math.ceil(self.width/self.number_v_cells)

        self.cells = {}
        for h in range(self.number_h_cells):
            for v in range(self.number_v_cells):
                self.cells[(h,v)] = pygame.Rect(self.cell_width*h-self.epsilon, 
                                                self.cell_height*v-self.epsilon,
                                                self.cell_width+2*self.epsilon,
                                                self.cell_height+2*self.epsilon)

    def intersects(self, rects):
        intersection = []
        for cell in self.cells.values():
            if cell.collidelist(rects) != -1:
                intersection.append(cell)
                #color = (int((cell.x/1000)*255), int((cell.y/1000)*255), ((cell.x*cell.y/1000)*255))
                #pygame.draw.rect(self.screen, color, cell,  width=0)
        return intersection

class TournamentVisualizer:
    def __init__(self):
        self.running = True
        self.size = (800,600)

        #create window
        self.background_color = (36,44,52)
        self.window = pygame.display.set_mode(self.size, pygame.DOUBLEBUF | pygame.HWSURFACE | pygame.RESIZABLE)
        
        # Drawing Sprite
        self.player = PlayerVisualizer(self.window, 200, 200)
        self.grid = Grid(self.window, self.size, (8, 8))

        # dragging
        self.dragging = False
        self.lastX = None 
        self.lastY = None

        #create window
        self.window.fill(self.background_color)
        pygame.display.flip()

    def on_cleanup(self):
        pygame.quit()
        
    def check_event(self,event):
        if event.type == pygame.QUIT:
            self.running = False
        
        elif event.type == pygame.VIDEORESIZE:
            self.window = pygame.display.set_mode(event.dict['size'], pygame.DOUBLEBUF | pygame.HWSURFACE | pygame.RESIZABLE)
        
        elif event.type == pygame.ACTIVEEVENT:
            pass

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4 or event.button == 5:
                zoom = 1.05 if event.button == 4 else 0.95
                mx, my = event.pos
                left   = mx + (self.player.left - mx) * zoom
                right  = mx + (self.player.right - mx) * zoom
                top    = my + (self.player.top - my) * zoom
                bottom = my + (self.player.bottom - my) * zoom
                self.player.move(left, top, right-left, bottom-top)

            if event.button == pygame.BUTTON_LEFT:  
                self.dragging = True     
                self.lastX, self.lastY = event.pos

        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False

        if self.dragging and event.type == pygame.MOUSEMOTION:
            mouse_x, mouse_y = event.pos
            offset_x = self.lastX - mouse_x
            offset_y = self.lastY - mouse_y
            left   = self.player.left - offset_x
            right  = self.player.right - offset_x
            top    = self.player.top - offset_y
            bottom = self.player.bottom - offset_y
            self.player.move_offset(-offset_x, -offset_y)
            self.lastX, self.lastY = event.pos

    def render(self):
        self.window.fill(self.background_color)
        rectangles = self.player.draw()
        grid_cells = self.grid.intersects(rectangles)
        pygame.display.update(grid_cells)

    def on_execute(self):
        while self.running == True:
            for event in pygame.event.get():
                self.check_event(event)
            self.render()
        self.on_cleanup()
    
class PlayerVisualizer:
    def __init__(self, screen, origin_x, origin_y) -> None:
        self.screen = screen

        # Dimension and position
        self.x = origin_x
        self.y = origin_y
        self.primary_width = 175
        self.seconday_width = 25
        self.primary_ratio = self.primary_width/(self.primary_width+self.seconday_width)
        self.secondary_ratio = self.seconday_width/(self.primary_width+self.seconday_width)
        height = 45

        # Rectangles
        self.primary_rect = pygame.Rect(origin_x+self.seconday_width, origin_y, self.primary_width, height)
        self.secondary_rect = pygame.Rect(origin_x, origin_y, self.seconday_width, height)

        # Colors
        self.primary_color = (88,89,94,255)
        self.secondary_color = (120,122,128,255)
        self.separator_color = (68,69,73,255)

        # Drawings
        self.epsilon = 2 # Otherwise, rounding errors causes rectangle to not be updated correctly
        self.line_threshold = 20 # If height is smaller than this, we don't draw the line

        self.__update_previous__()
        self.__update_sides__(origin_x, origin_y, (self.primary_width+self.seconday_width), height)

    def draw(self):
        border_radius = 5
        pygame.draw.rect(self.screen, self.primary_color, self.primary_rect,  width=0,
            border_top_right_radius=border_radius, border_bottom_right_radius=border_radius)

        pygame.draw.rect(self.screen, self.secondary_color, self.secondary_rect,  width=0,  
            border_top_left_radius=border_radius, border_bottom_left_radius=border_radius)

        if self.bottom-self.top >= self.line_threshold:
            pygame.draw.aaline(self.screen, self.separator_color, 
                (self.left+(self.right-self.left)*self.secondary_ratio, self.bottom-self.epsilon), 
                (self.left+(self.right-self.left)*self.secondary_ratio, self.top+self.epsilon))

        return [self.primary_rect, self.secondary_rect, self.previous_primary_rect, self.previous_secondary_rect]

    def move_offset(self, offset_x, offset_y):
        self.__update_previous__()
        self.primary_rect.x += offset_x
        self.primary_rect.y += offset_y
        self.secondary_rect.x += offset_x
        self.secondary_rect.y += offset_y
        self.__update_sides__(self.left+offset_x, self.top+offset_y, 
            self.right-self.left, self.bottom-self.top)

    def move(self, left, top, width, height):
        self.__update_previous__()
        self.__update_sides__(left, top, width, height)
        self.primary_rect = pygame.Rect(left+width*self.secondary_ratio, top, width*self.primary_ratio, height)
        self.secondary_rect = pygame.Rect(left, top, width*self.secondary_ratio, height)

    def __update_previous__(self):
        self.previous_primary_rect = self.primary_rect.copy()
        self.previous_secondary_rect = self.secondary_rect.copy()

    def __update_sides__(self, left, top, width, height):
        self.left = left
        self.right = left+width
        self.top = top
        self.bottom = top+height

start = TournamentVisualizer()
start.on_execute()