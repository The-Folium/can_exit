import pygame
from copy import deepcopy

# разрешение графического окна - в файле settings.py
from settings import screen_width, screen_height
from render import Renderer

# реализованы две версии функции: с визуализацией и без нее:
# can_exit_visual - с визуализацией
# can_exit_no_visual - без визуализации


def can_exit_visual(labyrinth: list, animation_speed=25) -> bool:
    """
    Функция визуализирует работу алгоритма поиска прохода в заданном лабиринте
    Возвращает True, если лабиринт имеет сквозной проход от левого верхнего до правого нижнего угла, False в противном случае

    :param labyrinth: list of lists
    :param animation_speed: int - число шагов в секунду
    :return: bool
    """

    height = len(labyrinth)-1
    width = len(labyrinth[0])-1

    # Данные анимаций
    max_water_level = 11
    max_red_level = 12
    max_trace_level = 10

    path_points = []
    stuck_counter = 0

    log = []
    status = "waiting for keypress"
    message = ["Press [Space] to start"]

    init = True

    # available statuses:
    # ------------------
    # "special" - для проходимого лабиринта 1х1
    # "waiting for keypress" - ждем нажания "Space" перед стартом
    # "searching" - распросранение волн
    # "wave got stuck" - хотя бы одна из волн заполнила все доступное простарнство => пути нет
    # "drawing path" - путь найден, происходит анимация пути
    # "path drawn" - путь нарисован
    # "path was not found" - все волны заполнили доступное простанство и не встретились
    # "done success" - успешный финал
    # "done fail" - неуспешный финал

    # inappropriate data
    if height < 0 or width < 0 or labyrinth[0][0] != 0 or labyrinth[height][width] != 0:
        log.append("Unable to init")
        message = ["Original labyrinth is inappropriate", "Press [ENTER] to proceed"]
        status = "done fail"
        init = False

    # special case
    if labyrinth == [[0]]:
        status = "special"
        init = False
        log.extend(["Single cell special case", "Path found"])
        message = ["Original labyrinth is a single empty cell", "Path obviously exists", "Press [ENTER] to proceed"]

    # мы не хотим повлиять на исходные данные
    labyrinth = deepcopy(labyrinth)

    class Wave:
        """
        Класс, реализующий волну. Два экземпляра этого класса, инициализированные в разных углах лабиринта, реализуют алгоритм.
        """

        surrounding = [(-1, 0), (1, 0), (0, 1), (0, -1)]

        def __init__(self, id: int, start_position: tuple):
            self.id = id
            self.frontier = [start_position]
            self.current_mark = 2
            self.way_found = False
            self.move_has_been_done = False
            self.mode = "regular"
            labyrinth[start_position[1]][start_position[0]] = {"wave_id": id,
                                                                 "phase": 1,
                                                                 "mode": self.mode,
                                                                 "stage": 0}
            self.turning_to_red_status = "did not start yet"

        def go(self) -> None:
            """
            Метод реализует итерацию распространения волны
            :return: None
            """
            nonlocal path_points

            self.move_has_been_done = False
            new_frontier = []
            for cell_x, cell_y in self.frontier:
                for shift_x, shift_y in Wave.surrounding:
                    new_x, new_y = cell_x + shift_x, cell_y + shift_y
                    if (0 <= new_x <= width) and (0 <= new_y <= height):

                        if labyrinth[new_y][new_x] == 0:
                            labyrinth[new_y][new_x] = {"wave_id": self.id,
                                                         "phase": self.current_mark,
                                                         "mode": "regular",
                                                         "stage": 0}

                            self.move_has_been_done = True
                            new_frontier.append((new_x, new_y))

                        if type(labyrinth[new_y][new_x]) is dict and labyrinth[new_y][new_x]["wave_id"] != self.id:
                            self.way_found = True
                            if not path_points:
                                path_points = [(cell_x, cell_y), (new_x, new_y)]

            if self.move_has_been_done:
                self.frontier = new_frontier
                self.current_mark += 1

        def is_water_raised(self) -> bool:
            for line in labyrinth:
                for item in line:
                    if type(item) == dict and item["wave_id"] == self.id and \
                            item["mode"] == "regular" and item["stage"] != max_water_level:
                        return False
            return True

        def init_turning_to_red(self) -> None:
            nonlocal stuck_counter, log, message

            if self.mode != "red":
                self.mode = "red"
                stuck_counter += 1
                log.append(f"wave {self.id} has stopped spreading")
                message = ["There's no path from one corner to another", f"Wave is turning {'red' if self.id == 1 else 'green'}",
                           "That means wave won't spread anymore"]

        def proceed_turning_to_red(self) -> None:
            turning_to_red_flag = False
            if not self.mode == "red":
                return

            for row in range(height + 1):
                for col in range(width + 1):
                    if type(labyrinth[row][col]) == dict and \
                            labyrinth[row][col]["wave_id"] == self.id and \
                            labyrinth[row][col]["mode"] == "regular" and \
                            labyrinth[row][col]["phase"] == self.current_mark:
                        labyrinth[row][col]["mode"] = "red"
                        labyrinth[row][col]["stage"] = 0
                    if type(labyrinth[row][col]) == dict and \
                            labyrinth[row][col]["wave_id"] == self.id and \
                            labyrinth[row][col]["mode"] == "red" and \
                            labyrinth[row][col]["stage"] < max_red_level:
                        labyrinth[row][col]["stage"] += 1
                        if self.turning_to_red_status == "did not start yet":
                            self.turning_to_red_status = "in progress"
                        turning_to_red_flag = True

            if self.current_mark > 0:
                self.current_mark -= 1

            if self.turning_to_red_status == "in progress" and not turning_to_red_flag:
                self.turning_to_red_status = "done"

    def is_way_found() -> bool:
        return init and (wave1.way_found or wave2.way_found)

    def raise_water_level() -> bool:
        """
        Поднимает уровень воды на 1 по всей карте для всех волн
        Возвращает False, если вся вода поднялась полностью
        :return: bool
        """

        raise_flag = False
        for row in range(height+1):
            for col in range(width+1):
                if type(labyrinth[row][col]) == dict and \
                        labyrinth[row][col]["mode"] == "regular" and\
                        labyrinth[row][col]["stage"] < max_water_level:

                    labyrinth[row][col]["stage"] += 1
                    raise_flag = True

        return raise_flag

    def proceed_trace() -> bool:
        """
        Функция реализует поиск и итерационную активацию одного из кратчайших путей в лабиринте
        Каждый вызов генерирует новые два шага пути
        Возвращает False, если весь путь найден, True, если путь еще в процессе отыскания
        :return: bool
        """

        trace_flag = False
        for index in range(2):
            col, row = path_points[index]
            if type(labyrinth[row][col]) == dict and \
                    labyrinth[row][col]["mode"] == "regular" and \
                    labyrinth[row][col]["stage"] == max_water_level:
                labyrinth[row][col]["mode"] = "trace"
                labyrinth[row][col]["stage"] = 0
                for shift_x, shift_y in Wave.surrounding:
                    new_x, new_y = col+shift_x, row+shift_y
                    if (0 <= new_x <= width) and (0 <= new_y <= height) and \
                            type(labyrinth[new_y][new_x]) == dict and \
                            labyrinth[new_y][new_x]["phase"] == labyrinth[row][col]["phase"] - 1 and \
                            labyrinth[new_y][new_x]["wave_id"] == labyrinth[row][col]["wave_id"]:
                        path_points[index] = (new_x, new_y)
                trace_flag = True
        return trace_flag

    def animate_trace() -> None:
        """
        Функция анимирует "всплытие" маркеров на поверхность. Продвигает маркеры на один шаг анимации по всей территории
        :return: None
        """
        nonlocal animate_trace_status
        trace_flag = False
        for row in range(height+1):
            for col in range(width+1):
                if type(labyrinth[row][col]) == dict and \
                        labyrinth[row][col]["mode"] == "trace" and \
                        labyrinth[row][col]["stage"] < max_trace_level:
                    labyrinth[row][col]["stage"] += 1
                    if animate_trace_status == "did not start yet":
                        animate_trace_status = "in progress"
                    trace_flag = True
        if animate_trace_status == "in progress" and not trace_flag:
            animate_trace_status = "done"

    # pygame setup
    pygame.init()
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption('Can exit')
    clock = pygame.time.Clock()

    block_size = int(min(80, 2*max(screen_height//(height+width+8), screen_width//(height+width+8)))//4)*4
    renderer = Renderer(screen, block_size)

    # system init - мы не создаем волны и не запускаем алгоритм, если лабиринт не валиден
    if init:
        wave1 = Wave(1, (0, 0))
        wave2 = Wave(2, (width, height))
        raise_water_level()

        animate_trace_status = "did not start yet"
        log.append("waiting for keypress")

    # Animation loop
    while True:

        # Processing Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and status == "waiting for keypress":
                    status = "searching"
                    log.append("waves are spreading")
                    message = ["algorithm is searching for path", "two waves are spreading"]

                if event.key == pygame.K_RETURN and (status[:4] == "done" or status == "special"):
                    pygame.quit()
                    return is_way_found()

                if event.key == pygame.K_UP:
                    if animation_speed < 10:
                        animation_speed += 2
                    elif animation_speed < 60:
                        animation_speed += 5

                if event.key == pygame.K_DOWN:
                    if animation_speed > 10:
                        animation_speed -= 5
                    elif animation_speed > 2:
                        animation_speed -= 2

        # Status control:
        if status in ["searching", "wave got stuck", "drawing path", "path drawn", "path was not found"] and init:
            wave1.go()
            wave2.go()

            if not is_way_found() and not wave1.move_has_been_done and wave1.is_water_raised():
                wave1.init_turning_to_red()
                status = "wave got stuck"

            if not is_way_found() and not wave2.move_has_been_done and wave2.is_water_raised():
                wave2.init_turning_to_red()
                status = "wave got stuck"

            if status == "wave got stuck":
                wave1.proceed_turning_to_red()
                wave2.proceed_turning_to_red()

                if wave1.turning_to_red_status == "done" and wave2.turning_to_red_status == "done":
                    status = "path was not found"

            if is_way_found() and status != "drawing path":
                status = "drawing path"
                log.extend(["Path found", "Drawing path"])
                message = ["Path found.", "Algorithm will animate the path"]

            if status == "drawing path":
                proceed_trace()
                animate_trace()
                if animate_trace_status == "done":
                    status = "path drawn"
                    log.append("Path has been drawn")

            raise_water_status = raise_water_level()

            if not raise_water_status and status in ["path drawn", "path was not found"]:
                if status == "path drawn":
                    status = "done success"
                else:
                    status = "done fail"
                log.append("Done")
                message = ["Press [ENTER] to proceed", "(this will close the current window)"]

        # render
        renderer.render(labyrinth, status)
        renderer.render_status(log, message, animation_speed, status)
        pygame.display.update()

        # speed control
        clock.tick(animation_speed)


def can_exit_no_visual(labyrinth: list) -> bool:
    """
    Функция, возвращающая True, если лабиринт имеет сквозной проход и False в противном случае.

    :param labyrinth: list of lists
    :return: bool
    """

    height = len(labyrinth) - 1
    width = len(labyrinth[0]) - 1

    # Обработка частных случаев
    if height < 0 or width < 0 or labyrinth[0][0] != 0 or labyrinth[height][width] != 0:
        return False
    if labyrinth == [[0]]:
        return True

    labyrinth = deepcopy(labyrinth)

    class Wave:
        """
        Класс, реализующий волну. Два экземпляра этого класса реализуют алгоритм.
        """

        surrounding = [(-1, 0), (1, 0), (0, 1), (0, -1)]

        def __init__(self, id: int, start_position: tuple):
            self.id = id
            self.frontier = [start_position]
            self.current_mark = 2
            self.way_found = False
            self.move_has_been_done = False
            labyrinth[start_position[1]][start_position[0]] = {"wave_id": id,
                                                                 "phase": 1}

        def go(self) -> None:
            """
            Метод реализует итерацию распространения волны
            :return: None
            """
            self.move_has_been_done = False
            new_frontier = []
            for cell_x, cell_y in self.frontier:
                for shift_x, shift_y in Wave.surrounding:
                    new_x, new_y = cell_x + shift_x, cell_y + shift_y
                    if (0 <= new_x <= width) and (0 <= new_y <= height):

                        if labyrinth[new_y][new_x] == 0:
                            labyrinth[new_y][new_x] = {"wave_id": self.id,
                                                         "phase": self.current_mark}

                            self.move_has_been_done = True
                            new_frontier.append((new_x, new_y))

                        if type(labyrinth[new_y][new_x]) is dict and labyrinth[new_y][new_x]["wave_id"] != self.id:
                            self.way_found = True

            if self.move_has_been_done:
                self.frontier = new_frontier
                self.current_mark += 1

    def is_way_found() -> bool:
        return wave1.way_found or wave2.way_found

    wave1 = Wave(1, (0, 0))
    wave2 = Wave(2, (width, height))

    while True:
        wave1.go()
        wave2.go()

        if is_way_found():
            return True
        if not wave1.move_has_been_done or not wave2.move_has_been_done:
            return False