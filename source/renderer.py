import pygame

class Block(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.terrain_surf = pygame.image.load("../sprites/grass.png").convert_alpha()
        self.water_surf = pygame.image.load("../sprites/water.png").convert_alpha()
        self.rect = self.terrain_surf.get_rect(topleft=(0, 0))

class Renderer:
    def __init__(self, screen):
        self.screen = screen
        self.block = Block()
        self.tiles = pygame.sprite.Group()

    def render(self, array):
        self.screen.fill("Black")
        self.tiles.empty()
        for row in range(len(array)):
            for col in range(len(array[0])):
                x, y = 512 + 25*col-25*row, 13*(row+col)
                if array[row][col] == 1:
                    self.block.image = self.block.terrain_surf
                    self.block.rect.topleft = (x, y)
                    self.screen.blit(self.block.image, self.block.rect)
                    # print(row, col)
                if type(array[row][col]) == list:
                    self.block.image = self.block.water_surf
                    self.block.rect.topleft = (x, y + 20 - array[row][col][2])
                    self.screen.blit(self.block.image, self.block.rect)
                    # print(row, col)


