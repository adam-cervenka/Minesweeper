# Adam Červenka
# 21/12/2020
# Minesweeper

import pygame
import sys
import random
import time

# Constants
FPS = 10
BOX_SIZE = 40
GAP_SIZE = 1
X_MARGIN = 100
Y_MARGIN = 100
BOARDWIDTH = 10
BOARDHEIGHT = 10
DIFFICULTY = 10
BASIC_FONT_SIZE = 30

MINES = BOARDWIDTH * BOARDHEIGHT * DIFFICULTY // 100
WINDOWWIDTH = 2 * X_MARGIN + BOARDWIDTH * (BOX_SIZE + GAP_SIZE) + GAP_SIZE
WINDOWHEIGHT = 2 * Y_MARGIN + BOARDHEIGHT * (BOX_SIZE + GAP_SIZE) + GAP_SIZE
BUTTON_SIZE = int(3 / 4 * min(X_MARGIN, Y_MARGIN))
LEFT_OF_RESTART_BUTTON = 0
TOP_OF_RESTART_BUTTON = 0
LEFT_OF_MODE_BUTTON = WINDOWWIDTH - BUTTON_SIZE
TOP_OF_MODE_BUTTON = 0

# Colors in RGB
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 165, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 128, 0)
PURPLE = (255, 0, 255)
CYAN = (0, 255, 255)
BROWN = (165, 42, 42)
GRAY = (142, 142, 142)
LIGHT_GRAY = (203, 203, 203)

BG_COLOR = WHITE
UNREVEALED_BOX_COLOR = GRAY
REVEALED_BOX_COLOR = LIGHT_GRAY
LINE_COLOR = BLACK
FLAG_COLOR = RED
COLORS_OF_NUMBERS = {0: REVEALED_BOX_COLOR, 1: BLUE, 2: GREEN, 3: RED, 4: PURPLE,
                     5: ORANGE, 6: YELLOW, 7: CYAN, 8: BROWN, 'X': BLACK}


def main(reveal=False, box_x=None, box_y=None):
    '''Main game function.'''
    global FPS_CLOCK, DISPLAY_SURFACE, BASIC_FONT, MODE, STATE, FIRST_MOVE, FLAGS

    pygame.init()
    FPS_CLOCK = pygame.time.Clock()
    DISPLAY_SURFACE = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    pygame.display.set_caption('Minesweeper')
    BASIC_FONT = pygame.font.Font('freesansbold.ttf', BASIC_FONT_SIZE)
    MODE = True  # True – revealing; False – putting flags down
    STATE = None  # None – game continues; True – you won; False – you lost (some mine got clicked)
    FIRST_MOVE = True
    FLAGS = 0

    # Matrices (BOARDWIDTH * BOARDHEIGHT)
    mines = get_mines_around(get_mine_boxes(MINES))
    revealed_boxes = [BOARDHEIGHT * [False] for _ in range(BOARDWIDTH)]
    flag_boxes = [BOARDHEIGHT * [False] for _ in range(BOARDWIDTH)]

    if reveal:  # Reveals the first box clicked before restart in the first move.
        start_time = time.time()
        revelation(box_x, box_y, mines, revealed_boxes, flag_boxes)
    draw_board(mines, revealed_boxes, flag_boxes, 0)

    pygame.display.update()

    while True:
        if FIRST_MOVE:
            start_time = time.time()

        for coordinates in check_for_event():
            if STATE is None:
                box_x, box_y = coordinates
                revelation(box_x, box_y, mines, revealed_boxes, flag_boxes)

        if STATE is None:
            check_for_win(mines, revealed_boxes)
            playing_time = time.time() - start_time
        draw_board(mines, revealed_boxes, flag_boxes, playing_time)

        pygame.display.update()
        FPS_CLOCK.tick(FPS)


def terminate():
    '''Closes the window and terminates the program.'''
    pygame.quit()
    sys.exit()


def check_for_event():
    '''Checks if user clicked any button.'''
    clicked_boxes = []

    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYUP and event.key == pygame.K_ESCAPE):
            terminate()
        elif event.type == pygame.MOUSEBUTTONUP:
            if get_box_clicked(event.pos) is not None:
                clicked_boxes.append(get_box_clicked(event.pos))

    return clicked_boxes


def get_mine_boxes(count):
    '''Randomly generates mines.'''
    mine_boxes = [BOARDHEIGHT * [False] for _ in range(BOARDWIDTH)]

    for i in range(count):
        while True:
            box_x, box_y = random.randint(0, BOARDWIDTH - 1), random.randint(0, BOARDHEIGHT - 1)
            if mine_boxes[box_x][box_y] is False:
                mine_boxes[box_x][box_y] = None
                break

    return mine_boxes


def get_mines_around(mines):
    '''Counts how many mines are around each box (0-8).'''
    for box_x in range(BOARDWIDTH):
        for box_y in range(BOARDHEIGHT):
            if mines[box_x][box_y] is False:
                count = 0
                boxes_around_coordinates = ((box_x - 1, box_y - 1), (box_x - 1, box_y), (box_x - 1, box_y + 1),  # 3 boxes on the left
                                            (box_x, box_y - 1), (box_x, box_y + 1),  # 2 boxes in the same column
                                            (box_x + 1, box_y - 1), (box_x + 1, box_y), (box_x + 1, box_y + 1))  # 3 boxes on the right

                for coordinates in boxes_around_coordinates:
                    if 0 <= coordinates[0] < BOARDWIDTH and 0 <= coordinates[1] < BOARDHEIGHT:
                        if mines[coordinates[0]][coordinates[1]] is None:
                            count += 1

                mines[box_x][box_y] = count

    return mines


def get_left_top_of_box(box_x, box_y):
    '''Returns the coordinates of the given box.'''
    x = X_MARGIN + box_x * (BOX_SIZE + GAP_SIZE) + GAP_SIZE
    y = Y_MARGIN + box_y * (BOX_SIZE + GAP_SIZE) + GAP_SIZE
    return x, y


def draw_box(box_x, box_y, mines_around, is_revealed, flag):
    '''Draws a box and eventually number or flag or mine on it.'''
    left, top = get_left_top_of_box(box_x, box_y)
    if is_revealed:
        pygame.draw.rect(DISPLAY_SURFACE, REVEALED_BOX_COLOR, (left, top, BOX_SIZE, BOX_SIZE))
        if mines_around is None:
            mines_around = 'X'
        text_surf = BASIC_FONT.render(str(mines_around), True, COLORS_OF_NUMBERS[mines_around])
        text_rect = text_surf.get_rect()
        text_rect.center = (left + BOX_SIZE // 2, top + BOX_SIZE // 2)
        DISPLAY_SURFACE.blit(text_surf, text_rect)
    else:
        pygame.draw.rect(DISPLAY_SURFACE, UNREVEALED_BOX_COLOR, (left, top, BOX_SIZE, BOX_SIZE))
        if flag:
            text_surf = BASIC_FONT.render('P', True, FLAG_COLOR)
            text_rect = text_surf.get_rect()
            text_rect.center = (left + BOX_SIZE // 2, top + BOX_SIZE // 2)
            DISPLAY_SURFACE.blit(text_surf, text_rect)
    if STATE is False:
        if flag and mines_around is not None:  # flag is wrong
            pygame.draw.line(DISPLAY_SURFACE, LINE_COLOR, (left, top), (left + BOX_SIZE, top + BOX_SIZE), 3)
            pygame.draw.line(DISPLAY_SURFACE, LINE_COLOR, (left + BOX_SIZE, top), (left, top + BOX_SIZE), 3)


def draw_grid():
    '''Draws a rectangle under the board.'''
    width = BOARDWIDTH * (BOX_SIZE + GAP_SIZE) + GAP_SIZE
    height = BOARDHEIGHT * (BOX_SIZE + GAP_SIZE) + GAP_SIZE
    pygame.draw.rect(DISPLAY_SURFACE, LINE_COLOR, (X_MARGIN, Y_MARGIN, width, height))


def draw_board(mines, is_revealed, flag_boxes, time):
    '''Draws the board.'''
    DISPLAY_SURFACE.fill(BG_COLOR)
    draw_restart_button()
    draw_mode_button()
    draw_timer(time)
    draw_grid()

    for box_x in range(BOARDWIDTH):
        for box_y in range(BOARDHEIGHT):
            draw_box(box_x, box_y, mines[box_x][box_y], is_revealed[box_x][box_y], flag_boxes[box_x][box_y])

    if STATE is None:
        draw_message(str(MINES - FLAGS))
    elif STATE:
        draw_message('CONGRATULATIONS!')
    else:
        draw_message('GAME OVER!')


def draw_restart_button():
    '''Draws a button for restart.'''
    pygame.draw.rect(DISPLAY_SURFACE, LINE_COLOR, (LEFT_OF_RESTART_BUTTON, TOP_OF_RESTART_BUTTON, BUTTON_SIZE, BUTTON_SIZE))
    pygame.draw.rect(DISPLAY_SURFACE, UNREVEALED_BOX_COLOR, (LEFT_OF_RESTART_BUTTON + GAP_SIZE, TOP_OF_RESTART_BUTTON + GAP_SIZE, BUTTON_SIZE - 2 * GAP_SIZE, BUTTON_SIZE - 2 * GAP_SIZE))
    text_surf = BASIC_FONT.render('«', True, LINE_COLOR)
    text_rect = text_surf.get_rect()
    text_rect.center = (LEFT_OF_RESTART_BUTTON + BUTTON_SIZE // 2, TOP_OF_RESTART_BUTTON + BUTTON_SIZE // 2)
    DISPLAY_SURFACE.blit(text_surf, text_rect)


def draw_mode_button():
    '''Draws a button for switching mode.'''
    pygame.draw.rect(DISPLAY_SURFACE, LINE_COLOR, (LEFT_OF_MODE_BUTTON, TOP_OF_MODE_BUTTON, BUTTON_SIZE, BUTTON_SIZE))
    pygame.draw.rect(DISPLAY_SURFACE, UNREVEALED_BOX_COLOR, (LEFT_OF_MODE_BUTTON + GAP_SIZE, TOP_OF_MODE_BUTTON + GAP_SIZE, BUTTON_SIZE - 2 * GAP_SIZE, BUTTON_SIZE - 2 * GAP_SIZE))
    if MODE:
        text_surf = BASIC_FONT.render('X', True, LINE_COLOR)
    else:
        text_surf = BASIC_FONT.render('P', True, FLAG_COLOR)
    text_rect = text_surf.get_rect()
    text_rect.center = (LEFT_OF_MODE_BUTTON + BUTTON_SIZE // 2, TOP_OF_MODE_BUTTON + BUTTON_SIZE // 2)
    DISPLAY_SURFACE.blit(text_surf, text_rect)


def draw_message(text):
    '''Draws a message about the state of the game.'''
    text_surf = BASIC_FONT.render(text, True, LINE_COLOR)
    text_rect = text_surf.get_rect()
    text_rect.center = (WINDOWWIDTH // 2, BUTTON_SIZE // 2)
    DISPLAY_SURFACE.blit(text_surf, text_rect)


def draw_timer(time):
    '''Draws the time of the game – minutes, seconds and tenths.'''
    text_surf = BASIC_FONT.render(str(int(time / 60)) + ':' + str(round(time % 60, 1)), True, LINE_COLOR)
    text_rect = text_surf.get_rect()
    text_rect.center = (WINDOWWIDTH // 2, WINDOWHEIGHT - BUTTON_SIZE // 2)
    DISPLAY_SURFACE.blit(text_surf, text_rect)


def get_box_clicked(mouse_coordinates):
    '''Returns the coordinates of clicked box, or executes restart, or switches mode.'''
    global MODE

    x, y = mouse_coordinates
    if LEFT_OF_RESTART_BUTTON < x < LEFT_OF_RESTART_BUTTON + BUTTON_SIZE and \
            TOP_OF_RESTART_BUTTON < y < TOP_OF_RESTART_BUTTON + BUTTON_SIZE:
        main()  # restart
    elif STATE is None and LEFT_OF_MODE_BUTTON < x < LEFT_OF_MODE_BUTTON + BUTTON_SIZE and \
            TOP_OF_MODE_BUTTON < y < TOP_OF_MODE_BUTTON + BUTTON_SIZE:
        MODE = not MODE
        return None
    box_x = (x - X_MARGIN) // (BOX_SIZE + GAP_SIZE)
    box_y = (y - Y_MARGIN) // (BOX_SIZE + GAP_SIZE)
    if 0 <= box_x < BOARDWIDTH and 0 <= box_y < BOARDHEIGHT:
        return box_x, box_y


def revelation(box_x, box_y, mines, revealed_boxes, flag_boxes):
    '''Reveals appropriate boxes or moves a flag.'''
    global FLAGS, FIRST_MOVE

    if MODE:
        if not flag_boxes[box_x][box_y]:  # Box with flag can't be revealed.
            boxes_around_coordinates = ((box_x - 1, box_y - 1), (box_x - 1, box_y), (box_x - 1, box_y + 1),  # 3 boxes on the left
                                        (box_x, box_y - 1), (box_x, box_y + 1),  # 2 boxes in the same column
                                        (box_x + 1, box_y - 1), (box_x + 1, box_y), (box_x + 1, box_y + 1))  # 3 boxes on the right
            if not revealed_boxes[box_x][box_y]:
                if mines[box_x][box_y] is None:  # Mine got clicked.
                    if not FIRST_MOVE:
                        game_over(mines, flag_boxes, revealed_boxes)
                        return None
                    else:
                        main(True, box_x, box_y)  # Restart – you can't lose in the first move.
                FIRST_MOVE = False
                revealed_boxes[box_x][box_y] = True
                if mines[box_x][box_y] == 0:
                    for coordinates in boxes_around_coordinates:
                        if 0 <= coordinates[0] < BOARDWIDTH and 0 <= coordinates[1] < BOARDHEIGHT:
                            if not revealed_boxes[coordinates[0]][coordinates[1]]:
                                revelation(coordinates[0], coordinates[1], mines, revealed_boxes, flag_boxes)
            else:
                flags_around = 0

                for coordinates in boxes_around_coordinates:
                    if 0 <= coordinates[0] < BOARDWIDTH and 0 <= coordinates[1] < BOARDHEIGHT:
                        if flag_boxes[coordinates[0]][coordinates[1]]:
                            flags_around += 1

                if flags_around > mines[box_x][box_y]:
                    game_over(mines, flag_boxes, revealed_boxes)
                if flags_around == mines[box_x][box_y]:  # Just all mines around the box are correct.
                    for coordinates in boxes_around_coordinates:
                        if 0 <= coordinates[0] < BOARDWIDTH and 0 <= coordinates[1] < BOARDHEIGHT:
                            if not revealed_boxes[coordinates[0]][coordinates[1]] and not flag_boxes[coordinates[0]][coordinates[1]]:
                                revelation(coordinates[0], coordinates[1], mines, revealed_boxes, flag_boxes)
    else:
        if not revealed_boxes[box_x][box_y]:
            if flag_boxes[box_x][box_y]:
                flag_boxes[box_x][box_y] = False  # removes flag
                FLAGS -= 1
            elif FLAGS < MINES:
                flag_boxes[box_x][box_y] = True  # puts flag
                FLAGS += 1


def game_over(mines, flag_boxes, revealed_boxes):
    '''Reveals all mines in the field and marks wrong placed flags'''
    global STATE

    STATE = False

    for box_x in range(BOARDWIDTH):
        for box_y in range(BOARDHEIGHT):
            if not flag_boxes[box_x][box_y] and mines[box_x][box_y] is None:
                revealed_boxes[box_x][box_y] = True


def check_for_win(mines, revealed_boxes):
    '''Checks if user won – if all boxes without mines are revealed.'''
    global STATE

    if sum(mines[box_x].count(None) for box_x in range(BOARDWIDTH)) + \
            sum(revealed_boxes[box_x].count(True) for box_x in range(BOARDWIDTH)) == BOARDWIDTH * BOARDHEIGHT:
        STATE = True


if __name__ == '__main__':
    main()
