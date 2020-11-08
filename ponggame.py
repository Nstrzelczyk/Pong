#! python3
# coding=utf-8

import pygame
import pygame.locals


class Board(object):
    """
    Game board. Responsible for drawing the game window.
    """

    def __init__(self, width, height):
        """
        Game board constructor.

        :param width:
        :param height:
        """
        self.surface = pygame.display.set_mode((width, height), 0, 32)
        pygame.display.set_caption('Simple Pong')

    def draw(self, *args):
        """
        Draws the game windows

        :param args: list of object to draw
        """
        background = (230, 220, 225)
        self.surface.fill(background)
        for drawable in args:
            drawable.draw_on(self.surface)

        pygame.display.update()


class PongGame(object):
    """
    Brings all the elements of the game together.
    """

    def __init__(self, width, height):
        pygame.init()
        self.board = Board(width, height)
        # the clock with we will use to control the speed off drawing
        # consecutive frames of the game
        self.fps_clock = pygame.time.Clock()
        self.ball = Ball(20, 20, width / 2, height / 2)
        self.player1 = Racket(width=80, height=20, x=width / 2 - 40, y=height - 40)
        self.player2 = Racket(width=80, height=20, x=width / 2 - 40, y=20, color=(0, 0, 0))
        self.ai = Ai(self.player2, self.ball)
        self.judge = Judge(self.board, self.ball, self.player2, self.ball)

    def run(self):
        pygame.key.set_repeat(50, 25)
        """
        Main program loop.
        """
        while not self.handle_events():
            # loop until receiving a signal to output.
            self.ball.move(self.board, self.player1)
            self.ball.move(self.board, self.player1, self.player2)
            self.board.draw(
                self.ball,
                self.player1,
                self.player2,
                self.judge,
            )
            self.ai.move()
            self.fps_clock.tick(30)

    def handle_events(self):
        """
        Handling system events.
        """
        for event in pygame.event.get():
            if event.type == pygame.locals.QUIT:
                pygame.quit()
                return True
            pygame.key.get_pressed()
            # capture cursor key presses
            if event.type == pygame.KEYDOWN:
                poz_x = self.player1.x
                poz_y = self.player2.x
                if event.key == pygame.K_LEFT:
                    self.player1.x -= 8
                elif event.key == pygame.K_RIGHT:
                    self.player1.x += 8
                self.player1.move(poz_x)

                # if event.key == pygame.K_a:
                #     self.player2.x -= 5
                # elif event.key == pygame.K_d:
                #     self.player2.x += 5
                # self.player2.move(poz_y)


class Drawable(object):
    """
    Base class for drawn objects
    """

    def __init__(self, width, height, x, y, color=(0, 255, 0)):
        self.width = width
        self.height = height
        self.color = color
        self.surface = pygame.Surface([width, height], pygame.SRCALPHA, 32).convert_alpha()
        self.rect = self.surface.get_rect(x=x, y=y)

    def draw_on(self, surface):
        surface.blit(self.surface, self.rect)


class Ball(Drawable):
    """
    The ball itself controls its speed and direction.
    """
    def __init__(self, width, height, x, y, color=(200, 10, 50), x_speed=3, y_speed=3):
        super(Ball, self).__init__(width, height, x, y, color)
        pygame.draw.ellipse(self.surface, self.color, [0, 0, self.width, self.height])
        self.x_speed = x_speed
        self.y_speed = y_speed
        self.start_x = x
        self.start_y = y

    def bounce_y(self):
        """
        Inverts the velocity vector on the Y axis.
        """
        self.y_speed *= -1

    def bounce_x(self):
        """
        Inverts the velocity vector on the X axis.
        """
        self.x_speed *= -1

    def reset(self):
        """
        Brings the ball to its initial position and inverts the velocity vector along the Y axis.
        """
        self.rect.move(self.start_x, self.start_y)
        self.bounce_y()

    def move(self,board, *args):
        """
        Moves the ball by the velocity vector.
        """
        self.rect.x += self.x_speed
        self.rect.y += self.y_speed

        if self.rect.x < 0 or self.rect.x > (board.surface.get_width() - self.width):
            self.bounce_x()

        if self.rect.y < self.height or self.rect.y > (board.surface.get_height() - self.height):
            self.bounce_y()

        for racket in args:
            if self.rect.colliderect(racket.rect):
                self.bounce_y()


class Racket(Drawable):
    """
    Racket, it moves along the X axis with a speed limit.
    """

    def __init__(self, width, height, x, y, color=(100, 200, 150), max_speed=10):
        super(Racket, self).__init__(width, height, x, y, color)
        self.max_speed = max_speed
        self.surface.fill(color)
        self.x = x

    def move(self, x):
        """
        Moves the racket to the designated place.
        """
        delta = x - self.rect.x
        if abs(delta) > self.max_speed:
            delta = self.max_speed if delta > 0 else - self.max_speed
        self.rect.x += delta


class Ai(object):
    """
    The opponent controls his racket on the basis of observing the ball.
    """
    def __init__(self, racket, ball):
        self.ball = ball
        self.racket = racket

    def move(self):
        x = self.ball.rect.centerx
        self.racket.move(x)


# TODO: Dostosować rakietke nie zawsze trafiała piłeczkę,
#  gdy self.ball.rect.centerx > od self.racet.centerx move + jak mniejsze move -
# TODO: sprawdzic czy rakietka ma centerx


class Judge(object):
    """
    Judge games.
    """

    def __init__(self, board, ball, *args):
        self.ball = ball
        self.board = board
        self.rackets = args
        self.score = [0, 0]

        # Font PyGame
        pygame.font.init()
        font_path = pygame.font.match_font('arial')
        self.font = pygame.font.Font(font_path, 64)

    def update_score(self, board_height):
        """
        Allocates the points and brings the ball to its original position.
        """
        if self.ball.rect.y <= self.ball.height :
            self.score[0] += 1
            self.ball.reset()
        elif self.ball.rect.y >= board_height - self.ball.height:
            self.score[1] += 1
            self.ball.reset()

    def draw_text(self, surface,  text, x, y):
        """
        Draws the indicated text at the indicated location
        """
        text = self.font.render(text, True, (150, 150, 150))
        rect = text.get_rect()
        rect.center = x, y
        surface.blit(text, rect)

    def draw_on(self, surface):
        """
        Draws the indicated text at the indicated location.
        """
        height = self.board.surface.get_height()
        self.update_score(height)

        width = self.board.surface.get_width()
        self.draw_text(surface, "Player: {}".format(self.score[0]), width/2, height * 0.3)
        self.draw_text(surface, "Computer: {}".format(self.score[1]), width/2, height * 0.7)


# This part should always be at the end of the module, we want to start our game only after all classes are declared.
if __name__ == "__main__":
    game = PongGame(800, 400)
    game.run()