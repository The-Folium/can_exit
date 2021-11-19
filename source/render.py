import pygame
from settings import *
from math import sin, cos, pi

class Block(pygame.sprite.Sprite):
    """
    Класс представляет изометрический блок. Конструктор загружает, конвертирует, масштабирует коллекцию спрайтов.
    """
    def __init__(self, block_size: int):
        super().__init__()
        self.terrain_surf = pygame.transform.smoothscale(pygame.image.load("../sprites/grass.png").convert_alpha(), (block_size, block_size))
        self.water_surf_list = []
        for n in range(11):
            self.water_surf_list.append(pygame.transform.smoothscale(pygame.image.load(f"../sprites/water_a{n}.png").convert_alpha(), (block_size, block_size)))

        self.red_surf_list = []
        for n in range(13):
            self.red_surf_list.append(pygame.transform.smoothscale(pygame.image.load(f"../sprites/red_a{n}.png").convert_alpha(), (block_size, block_size)))

        self.green_surf_list = []
        for n in range(13):
            self.green_surf_list.append(pygame.transform.smoothscale(pygame.image.load(f"../sprites/green_a{n}.png").convert_alpha(), (block_size, block_size)))
        self.bedrock_surf = pygame.transform.smoothscale(pygame.image.load("../sprites/bedrock.png").convert_alpha(), (block_size, block_size))

        self.path_surf = pygame.transform.smoothscale(pygame.image.load("../sprites/mark2.png").convert_alpha(), (block_size, block_size))
        self.s_surf = pygame.transform.smoothscale(pygame.image.load("../sprites/s.png").convert_alpha(), (block_size, block_size))
        self.f_surf = pygame.transform.smoothscale(pygame.image.load("../sprites/f.png").convert_alpha(), (block_size, block_size))

        self.rect = self.terrain_surf.get_rect(topleft=(0, 0))

class Renderer:
    """
    Класс Renderer - модуль отрисовки изометрического мира, предоставляет методы:

    render() - отрисовывает весь изометрический мир
    render_status() - отрисовывает весь пояснительный текст
    """

    def __init__(self, screen, block_size: int):
        self.screen = screen
        self.block_size = block_size
        self.block = Block(block_size)
        self.font = pygame.font.Font('../font/Chava-Regular.ttf', 20)
        self.jump = 0
        self.jump_speed = 0.2
        self.blink_counter = 0

    def render(self, labyrinth: list, status: str) -> None:
        self.screen.fill("Black")
        height = len(labyrinth)
        width = len(labyrinth[0])

        def draw_start_marker() -> None:
            x, y = (screen_width - (height + width + 1) * self.block_size // 2) // 2, screen_height // 2 - self.block_size // 2 * (1 - 0.5 * sin(self.jump))
            self.block.image = self.block.s_surf
            self.block.rect.topleft = (x, y)
            self.screen.blit(self.block.image, self.block.rect)

        def draw_finish_marker() -> None:
            x, y = (screen_width - (height + width + 1) * self.block_size // 2) //2 + (height + width-2) * (self.block_size//2-1), screen_height//2 + (height-width) * (self.block_size//4-1) - self.block_size // 2 * (1 - 0.5 * cos(self.jump)) + 1
            self.block.image = self.block.f_surf
            self.block.rect.topleft = (x, y)
            self.screen.blit(self.block.image, self.block.rect)

        for col in range(width-1, -1, -1):
            for row in range(height):

                x, y = (screen_width - (height + width + 1) * self.block_size // 2) //2 + (col+row) * (self.block_size//2-1), screen_height//2 + (row-col) * (self.block_size//4-1)

                self.block.image = self.block.bedrock_surf
                self.block.rect.topleft = (x, y)
                self.screen.blit(self.block.image, self.block.rect)

        for col in range(width-1, -1, -1):
            for row in range(height):

                x, y = (screen_width - (height + width + 1) * self.block_size // 2) //2 + (col+row) * (self.block_size//2-1), screen_height//2 + (row-col) * (self.block_size//4-1) - self.block_size//2 + 1

                # terrain
                if labyrinth[row][col] == 1:
                    self.block.image = self.block.terrain_surf
                    self.block.rect.topleft = (x, y)
                    self.screen.blit(self.block.image, self.block.rect)

                # spreading water
                if status != "waiting for keypress" and type(labyrinth[row][col]) == dict and labyrinth[row][col]["mode"] == "regular":
                    self.block.image = self.block.water_surf_list[labyrinth[row][col]["stage"] - 1]
                    self.block.rect.topleft = (x, y)
                    self.screen.blit(self.block.image, self.block.rect)

                # stuck water
                if type(labyrinth[row][col]) == dict and labyrinth[row][col]["mode"] == "red":
                    if labyrinth[row][col]["wave_id"] == 1:
                        self.block.image = self.block.red_surf_list[labyrinth[row][col]["stage"]]
                    else:
                        self.block.image = self.block.green_surf_list[labyrinth[row][col]["stage"]]
                    self.block.rect.topleft = (x, y)
                    self.screen.blit(self.block.image, self.block.rect)

                # drawing path
                def draw_marker() -> None:
                    self.block.image = self.block.path_surf
                    self.block.rect.topleft = (x, y + 10 - labyrinth[row][col]["stage"])
                    self.screen.blit(self.block.image, self.block.rect)

                def draw_water() -> None:
                    self.block.image = self.block.water_surf_list[10]
                    self.block.rect.topleft = (x, y)
                    self.screen.blit(self.block.image, self.block.rect)

                if type(labyrinth[row][col]) == dict and labyrinth[row][col]["mode"] == "trace":
                    if labyrinth[row][col]["stage"] < 10:
                        draw_marker()
                        draw_water()
                    else:
                        draw_water()
                        draw_marker()

                # jumping S- and F-markers
                if status in ["waiting for keypress", "special"] and col == 0 and row == 0:
                    draw_start_marker()

                if status in ["waiting for keypress", "special"] and col == width - 1 and row == height - 1:
                    draw_finish_marker()
                    self.jump += self.jump_speed
                    if self.jump > 2 * pi:
                        self.jump -= 2 * pi

    def render_status(self, log: list, message: list, animation_speed: int, status: str) -> None:

        # LEFT-BOTTOM - animation speed
        stat_surf = self.font.render("[UP], [DOWN] - adjust animation speed (2..60)", False, "grey")
        stat_rect = stat_surf.get_rect(topleft=(10, screen_height-60))
        self.screen.blit(stat_surf, stat_rect)

        stat_surf = self.font.render("Current speed (steps/sec): "+str(animation_speed), False, "white")
        stat_rect = stat_surf.get_rect(topleft=(10, screen_height-30))
        self.screen.blit(stat_surf, stat_rect)

        # CONCLUSION
        stat_surf = self.font.render("Conclusion:", False, "grey")
        stat_rect = stat_surf.get_rect(topleft=(screen_width - 250, screen_height - 60))
        self.screen.blit(stat_surf, stat_rect)

        if status in ["drawing path", "path drawn", "done success", "special"]:
            stat_surf = self.font.render("PATH FOUND", False, "green")
        elif status in ["waiting for keypress", "searching"]:
            stat_surf = self.font.render("UNKNOWN", False, "yellow")
        elif status in ["wave got stuck", "path was not found", "done fail"]:
            stat_surf = self.font.render("THERE IS NO PATH", False, "red")

        stat_rect = stat_surf.get_rect(topleft=(screen_width - 250, screen_height - 30))
        self.screen.blit(stat_surf, stat_rect)

        # LOG
        stat_surf = self.font.render("LOG", False, "grey")
        stat_rect = stat_surf.get_rect(topleft=(10, 10))
        self.screen.blit(stat_surf, stat_rect)

        for index, entry in enumerate(log):
            stat_surf = self.font.render("> "+ entry, False, "green")
            stat_rect = stat_surf.get_rect(topleft=(10,40 + index*20))
            self.screen.blit(stat_surf, stat_rect)

        # MESSAGE
        for index, entry in enumerate(message):

            # мерцает, если строка содержит инструкцию к нажатию клавиши
            if "[" not in entry or animation_speed // 4 < self.blink_counter:
                stat_surf = self.font.render(entry, False, "yellow")
                stat_rect = stat_surf.get_rect(topleft=(0,0))
                stat_rect.topleft=(screen_width - stat_rect.width - 20, 10 + index*20)
                self.screen.blit(stat_surf, stat_rect)

        self.blink_counter += 1
        if self.blink_counter > animation_speed//2:
            self.blink_counter = 0