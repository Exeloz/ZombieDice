import pygame
from pygame.locals import *
import os

class App:
    def __init__(self):
        self.running = True
        self.size = (800,600)

         #create window
        self.window = pygame.display.set_mode(self.size, pygame.DOUBLEBUF | pygame.HWSURFACE | pygame.RESIZABLE)

        #create car_
        currentdir = os.path.dirname(os.path.realpath(__file__))
        imagedir = currentdir+'/download.jpg'
        self.car_ =  pygame.image.load(imagedir)
        self.car_rect = self.car_.get_rect(center = self.window.get_rect().center)
        self.blit()
        
        # dragging
        self.dragging = False
        self.lastX = None 
        self.lastY = None

        #create window
        pygame.display.flip()

    def blit(self):
        self.car_surface = pygame.transform.smoothscale(self.car_, self.car_rect.size)
        self.window.fill(0)
        self.window.blit(self.car_surface, self.car_rect)

    def on_init(self):
        self.country = Country()

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
                left   = mx + (self.car_rect.left - mx) * zoom
                right  = mx + (self.car_rect.right - mx) * zoom
                top    = my + (self.car_rect.top - my) * zoom
                bottom = my + (self.car_rect.bottom - my) * zoom
                self.car_rect = pygame.Rect(left, top, right-left, bottom-top)

            if event.button == pygame.BUTTON_LEFT:  
                self.dragging = True     
                self.lastX, self.lastY = event.pos

        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False

        if self.dragging and event.type == pygame.MOUSEMOTION:
            mouse_x, mouse_y = event.pos
            offset_x = self.lastX - mouse_x
            offset_y = self.lastY - mouse_y
            self.car_rect.x -= offset_x
            self.car_rect.y -= offset_y
            self.lastX, self.lastY = event.pos

        self.blit()

        pygame.display.update()

    def on_execute(self):
        while self.running == True:
            for event in pygame.event.get():
                self.check_event(event)
        self.on_cleanup()

class Country(App):
    def __init__(self):
        super().__init__()
    

start = App()
start.on_init()
start.on_execute()