# import kivy libraries
import random

from kivy.app import App
from kivy.clock import Clock
from kivy.properties import NumericProperty, ReferenceListProperty, ObjectProperty
from kivy.uix.widget import Widget
from kivy.vector import Vector


class Menu(Widget):
    pass

class PongBall(Widget):

    # velocity of the ball on x, y axis
    velocity_x = NumericProperty(0)
    velocity_y = NumericProperty(0)

    # shorthand for ball velocity
    velocity = ReferenceListProperty(velocity_x, velocity_y)

    # animating ball movement
    def move(self):
        self.pos = Vector(*self.velocity) + self.pos

class PongPaddle(Widget):

    score = NumericProperty(0)

    def bounce_ball(self, ball):
        if self.collide_widget(ball):
            vx, vy = ball.velocity
            offset = (ball.center_x - self.center_x) / (self.height / 2)
            bounced = Vector(vx, -1 * vy)
            vel = bounced
            ball.velocity = vel.x + offset, vel.y

# creating arena, ball and pads
class PongGame(Widget):
    ball = ObjectProperty(None)
    player1 = ObjectProperty(None)
    player2 = ObjectProperty(None)
    menu1 = ObjectProperty(None)

    # Proud of this! Made a new method to reset the court instead of serving immediately.
    def reset_court(self):
        self.ball.center = self.center
        self.ball.velocity = (0,0)

    #reset court and score
    def reset_game(self):
        self.ball.center = self.center
        self.ball.velocity = (0,0)

        self.player1.center_x = self.center_x
        self.player2.center_x = self.center_x

        self.player1.score = 0
        self.player2.score = 0


    def serve_ball(self, dt, vel=(0,0)):
        vel = (random.randrange(-5,5), random.choice([-4,4]))
        self.ball.center = self.center
        self.ball.velocity = vel
       # self.player1.center_x = self.center_x
       # self.player2.center_x = self.center_x

    def update(self, dt):
        self.ball.move()

        # bounce off paddles
        self.player1.bounce_ball(self.ball)
        self.player2.bounce_ball(self.ball)

        # floor and ceiling points
        if (self.ball.y < self.y):
            self.player2.score += 1
            self.reset_court()

            if self.player2.score < 5:
                Clock.schedule_once(self.serve_ball, 2)

            else:
                pass
                #post game menu


        if (self.ball.top > self.top):
            self.player1.score += 1
            self.reset_court()

            if self.player1.score < 5:
                Clock.schedule_once(self.serve_ball, 2)

            else:
                pass
                #Add post game menu



        # bounce off walls
        if (self.ball.x < self.x) or (self.ball.right > self.width):
            self.ball.velocity_x *= -1

    # touch move keeps the paddles inside the window

    def on_touch_move(self, touch):
        if touch.y < self.height // 2 and touch.x > (self.x + self.player1.width // 2) and touch.x < (self.width - self.player1.width // 2):
            self.player1.center_x = touch.x
        if touch.y > self.height - self.height // 2 and touch.x > (self.x + self.player1.width // 2) and touch.x < (self.width - self.player1.width // 2):
            self.player2.center_x = touch.x


# building main app
class PongAIApp(App):
    def build(self):
        game = PongGame()
        #Clock.schedule_once(game.serve_ball, 2)
        Clock.schedule_interval(game.update, 1.0/60.0)
        return game

# running the application
if __name__ == '__main__':
    PongAIApp().run()
