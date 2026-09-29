"""Escala proporcional e coordenadas de mouse independentes da resolução."""
import pygame


class Viewport:
    def __init__(self,size):
        self.resize(size)

    def resize(self,size):
        scale=min(size[0]/1280,size[1]/720)
        self.size=(max(1,round(1280*scale)),max(1,round(720*scale)))
        self.offset=((size[0]-self.size[0])//2,(size[1]-self.size[1])//2)
        self.target=pygame.Surface(self.size)

    def to_logical(self,position):
        return pygame.Vector2((position[0]-self.offset[0])*1280/self.size[0],
                              (position[1]-self.offset[1])*720/self.size[1])

    def present(self,logical,window):
        if self.offset!=(0,0) or self.size!=window.get_size(): window.fill((0,0,0))
        if self.size==(1280,720): window.blit(logical,self.offset)
        else:
            pygame.transform.smoothscale(logical,self.size,self.target)
            window.blit(self.target,self.offset)
