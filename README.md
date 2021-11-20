# Кодинг-марафон. Задача 10. "can_exit"

Для работы кода необходим установленный pygame:
```
pip install pygame
```

## Описание файлов проекта
```
sprites/           - папка со спрайтами
source/main.py     - содержит реализацию двух версий алгоритма: can_exit_visual и can_exit_non_visual
source/render.py   - классы Block (спрайты) и Renderer (весь инструментарий отрисовки)
source/settings.py - настройки разрешения графического окна
```

Запускаемые файлы:
```
source/demo.py     - запускаемый скрипт, демонстрационный режим
source/tests.py    - запускаемый скрипт, запуск юниттестов функции без визуализации
```
---
## Управление в графическом режиме:

```
[SPACE]     - начать визуализацию
[ENTER]     - выход, если алгоритм отработал
[UP]/[DOWN] - настройка скорости анимации
```

## Интерфейс графического режима:

![hints](https://user-images.githubusercontent.com/63975541/142675577-30fa41e8-ca9e-48f2-b606-887c529c388a.jpg)

## Видеофрагмент работы деморежима:

https://user-images.githubusercontent.com/63975541/142672980-82496901-e118-4048-abc9-3725ccb30374.mp4

