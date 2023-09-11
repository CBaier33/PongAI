# import kivy libraries
import random
import os
import neat
import time
import pickle

from kivy.app import App
from kivy.clock import Clock
from kivy.properties import NumericProperty, ReferenceListProperty, ObjectProperty
from kivy.uix.widget import Widget
from kivy.vector import Vector


class Menu(Widget):
    pass


class GameInformation:
    def __init__(self, player1_hits, player2_hits, player1_score, player2_score):
        self.player1_hits = player1_hits
        self.player2_hits = player2_hits
        self.player1_score = player1_score
        self.player2_score = player2_score

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

    hits = NumericProperty(0)

    def bounce_ball(self, ball):
        if self.collide_widget(ball):
            self.hits += 1
            vx, vy = ball.velocity
            offset = (ball.center_x - self.center_x) / (self.height / 2)
            bounced = Vector(vx, -1 * vy)
            vel = bounced
            ball.velocity = vel.x + offset, vel.y

    
    def move(self, right=True):

        if right == True:
            self.center_x += 7

        elif right == False:
            self.center_x -= 7


# creating arena, ball and pads
class PongGame(Widget):
    ball = ObjectProperty(None)
    player1 = ObjectProperty(None)
    player2 = ObjectProperty(None)

    # Created a new method to reset the court instead of serving immediately.
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

    def serve_ball(self, dt):
        vel = (random.randrange(-5,5), random.choice([-4,4]))
        self.ball.center = self.center
        self.ball.velocity = vel

    def game_loop(self):

        self.ball.move()

        # bounce off paddles
        self.player1.bounce_ball(self.ball)
        self.player2.bounce_ball(self.ball)

        if (self.ball.y < self.y):
            self.player2.score += 1
            self.serve_ball()
           
        elif (self.ball.top > self.top):
            self.player1.score += 1
            self.serve_ball()

        if self.ball.x < self.x or self.ball.x > self.width - self.ball.width:
            self.ball.velocity_x *= -1


        game_info = GameInformation(self.player1.hits, self.player2.hits, self.player1.score, self.player2.score)

        return game_info 


    def update(self, dt, net2):
        self.ball.move()

        # bounce off paddles
        self.player1.bounce_ball(self.ball)
        self.player2.bounce_ball(self.ball)

        # floor and ceiling points
        if (self.ball.y < self.y):
            self.player2.score += 1
            self.serve_ball()

            #self.reset_court()
            #if self.player2.score < 5:
            #Clock.schedule_once(self.serve_ball, 2)

            #post game menu


        if (self.ball.top > self.top):
            self.player1.score += 1
            self.serve_ball()
            #self.reset_court()

            #if self.player1.score < 5:
            #Clock.schedule_once(self.serve_ball, 2)

            #else:
                #pass
        
       #Add post game menu?

        # bounce off walls
        if ((self.ball.x) < root.x) or ((self.ball.width) > root.width-self.ball.width):
            self.ball.velocity_x *= -1

    # touch move keeps the paddles inside the window

    def on_touch_move(self, touch):
        if touch.y < self.height // 2 and touch.x > (self.x + self.player1.width // 2) and touch.x < (self.width - self.player1.width // 2):
            self.player1.center_x = touch.x
        #if touch.y > self.height - self.height // 2 and touch.x > (self.x + self.player1.width // 2) and touch.x < (self.width - self.player1.width // 2):
        #    self.player2.center_x = touch.x

    def move_paddle(self, player1=True, right=True):
        if player1==True:
            if right == True and self.player1.center_x + 7 > self.width-(self.player1.width/2):
                return False
            if right == False and self.player1.center_x - 7  < self.x + (self.player1.width/2):
                return False

            self.player1.move(right)

        else:   
            if right == True and self.player2.center_x + 7 > self.width-(self.player2.width/2):
                return False
            if right == False and self.player2.center_x - 7 < self.x + (self.player2.width/2):
                return False
            self.player2.move(right)

    def aiVSai(self, dt):

        output1 = self.net1.activate((self.player1.center_x, self.ball.x, abs(self.player1.y-self.ball.top)))

        decision1 = output1.index(max(output1))

        if decision1 == 0:
            pass

        elif decision1 == 1:
            self.move_paddle(player1=True, right=True)

        else:
            self.move_paddle(player1=True, right=False)

        
        output2 = self.net2.activate((self.player2.center_x, self.ball.x, abs(self.player2.y-self.ball.top)))

        decision2 = output2.index(max(output2))

        if decision2 == 0:
            pass

        elif decision2 == 1:
            self.move_paddle(player1=False, right=True)

        else:
            self.move_paddle(player1=False, right=False)

        output2 = self.net2.activate((self.player2.center_x, self.ball.x, abs(self.player2.y-self.ball.top)))

        decision2 = output2.index(max(output2))

        if decision2 == 0:
            pass

        elif decision2 == 1:
            self.move_paddle(player1=False, right=True)

        else:
            self.move_paddle(player1=False, right=False)

        self.ball.move()

        # bounce off paddles
        self.player1.bounce_ball(self.ball)
        self.player2.bounce_ball(self.ball)

        if (self.ball.y < self.y):
            self.player2.score += 1
            self.reset_court()
            Clock.schedule_once(self.serve_ball, 2)
           
        elif (self.ball.top > self.top):
            self.player1.score += 1
            self.reset_court()
            Clock.schedule_once(self.serve_ball, 2)

        if self.ball.x < self.x or self.ball.x > self.width - self.ball.width:
            self.ball.velocity_x *= -1


        


    def ai_loop(self, dt):

        output2 = self.net2.activate((self.player2.center_x, self.ball.x, abs(self.player2.y-self.ball.top)))

        decision2 = output2.index(max(output2))

        if decision2 == 0:
            pass

        elif decision2 == 1:
            self.move_paddle(player1=False, right=True)

        else:
            self.move_paddle(player1=False, right=False)

        self.ball.move()

        # bounce off paddles
        self.player1.bounce_ball(self.ball)
        self.player2.bounce_ball(self.ball)

        if (self.ball.y < self.y):
            self.player2.score += 1
            self.reset_court()
            Clock.schedule_once(self.serve_ball, 2)
           
        elif (self.ball.top > self.top):
            self.player1.score += 1
            self.reset_court()
            Clock.schedule_once(self.serve_ball, 2)

        if self.ball.x < self.x or self.ball.x > self.width - self.ball.width:
            self.ball.velocity_x *= -1

    def play_ai(self, genome, config):

        self.net1 = neat.nn.FeedForwardNetwork.create(genome, config)
        self.net2 = neat.nn.FeedForwardNetwork.create(genome, config)


    def train_ai(self, genome1, genome2, config):
        net1 = neat.nn.FeedForwardNetwork.create(genome1, config)
        net2 = neat.nn.FeedForwardNetwork.create(genome2, config)
        run = True

        self.serve_ball()

        while True:

            output1 = net1.activate((self.player1.center_x, self.ball.x, abs(self.player1.y-self.ball.top)))
            decision1 = output1.index(max(output1))

            if decision1 == 0:
                pass

            elif decision1 == 1:
                self.move_paddle(player1=True, right=True)

            else:
                self.move_paddle(player1=True, right=False)

            output2 = net2.activate((self.player2.center_x, self.ball.x, abs(self.player2.y-self.ball.top)))
            decision2 = output2.index(max(output2))
            

            if decision2 == 0:
                pass

            elif decision2 == 1:
                self.move_paddle(player1=False, right=True)

            else:
                self.move_paddle(player1=False, right=False)

            game_info = self.game_loop()


            if game_info.player2_score >= 1 or game_info.player1_score >= 1 or game_info.player1_hits > 50 or game_info.player2_hits > 50:
                self.calculate_fitness(genome1, genome2, game_info)
                break


    def calculate_fitness(self, genome1, genome2, game_info): 
        genome1.fitness += game_info.player1_hits 
        genome2.fitness += game_info.player2_hits

# building main app
class pongaiApp(App):

    def build(self):
        
        local_dir = os.path.dirname(__file__)
        config_path = os.path.join(local_dir, "config.txt")

        config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                             neat.DefaultSpeciesSet, neat.DefaultStagnation,
                             config_path)

        #self.run_neat(config)
        winner = self.load_ai(config)

        game = PongGame()
        game.play_ai(winner, config)
        Clock.schedule_once(game.serve_ball, 2)
        #Clock.schedule_interval(game.ai_loop, (1.0/60.0))
        Clock.schedule_interval(game.aiVSai, (1.0/60.0))

        return game

    def run_neat(self, config):
        #p = neat.Checkpointer.restore_checkpoint('neat-checkpoint-49')
        p = neat.Population(config)
        p.add_reporter(neat.StdOutReporter(True))
        stats = neat.StatisticsReporter()
        p.add_reporter(stats)
        p.add_reporter(neat.Checkpointer(1))

        winner = p.run(self.eval_genomes, 5)
        print('winner: ',winner)

        with open("best.pickle", "wb") as best:
            pickle.dump(winner, best)


    def load_ai(self, config):
        with open("best.pickle", "rb") as best:
            winner = pickle.load(best)

        return winner


    def eval_genomes(self, genomes, config):

        for i, (genome_id1, genome1) in enumerate(genomes):
            if i == len(genomes) - 1:
                break
            genome1.fitness = 0
            for genome_id2, genome2  in genomes[i+1:]:
                genome2.fitness = 0 if genome2.fitness == None else genome2.fitness
                game = PongGame()
                game.train_ai(genome1, genome2, config)


# running the application
if __name__ == '__main__':
    pongaiApp().run()
