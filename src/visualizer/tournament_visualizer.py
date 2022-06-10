import pygame
from pygame.locals import *
import os

class App:
    def __init__(self):
        self.running = True
        self.size = (800,600)

        #create window
        self.window = pygame.display.set_mode(self.size, pygame.DOUBLEBUF | pygame.HWSURFACE | pygame.RESIZABLE)
        
        # Drawing Sprite
        self.test = TournamentPlayer(self.window, 'src/visualizer/nyan.gif', 200, 200)

        # dragging
        self.dragging = False
        self.lastX = None 
        self.lastY = None

        #create window
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
                left   = mx + (self.test.left - mx) * zoom
                right  = mx + (self.test.right - mx) * zoom
                top    = my + (self.test.top - my) * zoom
                bottom = my + (self.test.bottom - my) * zoom
                self.test.move(left, top, right-left, bottom-top)

            if event.button == pygame.BUTTON_LEFT:  
                self.dragging = True     
                self.lastX, self.lastY = event.pos

        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False

        if self.dragging and event.type == pygame.MOUSEMOTION:
            mouse_x, mouse_y = event.pos
            offset_x = self.lastX - mouse_x
            offset_y = self.lastY - mouse_y
            left   = self.test.left - offset_x
            right  = self.test.right - offset_x
            top    = self.test.top - offset_y
            bottom = self.test.bottom - offset_y
            self.test.move_offset(-offset_x, -offset_y)
            self.lastX, self.lastY = event.pos

    def render(self):
        self.window.fill(0)
        self.test.blit()
        pygame.display.update([self.test.sprite_rect, self.test.previous_rect])

    def on_execute(self):
        while self.running == True:
            for event in pygame.event.get():
                self.check_event(event)
            self.render()
        self.on_cleanup()
    
class TournamentPlayer:
    def __init__(self, screen, image_filename, origin_x, origin_y) -> None:
        self.screen = screen
        self.sprite = pygame.image.load(image_filename).convert_alpha()
        self.sprite_rect = self.sprite.get_rect(center = self.screen.get_rect().center)
        self.x = origin_x
        self.y = origin_y

        self.blit()
        self.__update_previous__()
        self.__update_sides__()

    def blit(self):
        self.sprite_surface = pygame.transform.smoothscale(self.sprite, self.sprite_rect.size)
        self.__update_sides__()
        self.screen.blit(self.sprite_surface, self.sprite_rect)

    def move_offset(self, offset_x, offset_y):
        self.__update_previous__()
        self.sprite_rect.x += offset_x
        self.sprite_rect.y += offset_y
        self.__update_sides__()

    def move(self, left, top, width, height):
        self.__update_previous__()
        self.sprite_rect = pygame.Rect(left, top, width, height)
        self.__update_sides__()

    def __update_previous__(self):
        self.previous_rect = self.sprite_rect.copy()

    def __update_sides__(self):
        self.left = self.sprite_rect.left
        self.right = self.sprite_rect.right
        self.top = self.sprite_rect.top
        self.bottom = self.sprite_rect.bottom

start = App()
start.on_execute()