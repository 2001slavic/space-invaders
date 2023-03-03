import pygame
import sys
import random


# Rulat cu success pe Windows 10 64-bit
# Python 3.9.0 64-bit
# pygame 2.0.0
# SDL 2.0.12

class Base:
    WIDTH = 800
    HEIGHT = 600
    FPS = 60
    GAME_OVER = False
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    caption = pygame.display.set_caption("Space Invaders")
    clock = pygame.time.Clock()
    def main():
        timer = 0
        sp_timer = 0
        most_down = 0
        running = True
        pygame.init()
        pygame.font.init()
        Enemy.make() # make initial set of enemies
        Bunker_Block.make() # make initial set of bunkers
        while running:
            if (most_down + Enemy.SIZE + Missile.HEIGHT >= Bunker_Block.y) | (Player.LIVES <= 0):
                Base.GAME_OVER = True
                Base.over()

            timer += 1
            if (Player.sp_trigger):
                sp_timer += 1
                if (sp_timer >= Player.SPAWN_PROTECTION * Base.FPS):
                    sp_timer = 0
                    Player.sp_trigger = False
            keys_pressed = pygame.key.get_pressed()
            if keys_pressed[pygame.K_a] & (Player.x != 0): # move player left
                Player.x -= Player.SPEED
            if keys_pressed[pygame.K_d] & (Player.x + Player.WIDTH + Player.SPEED <= Base.WIDTH): # move player right
                Player.x += Player.SPEED
            if keys_pressed[pygame.K_SPACE] & (Missile.player_exist == False): #shoot, makes only 1 possible player missile on map
                Missile.create_player(Player.x)
            for event in pygame.event.get():   #
                if event.type == pygame.QUIT:  #
                    running = False            # quit game
                    pygame.quit()              #
                    sys.exit()                 #
            if (Missile.player_exist):
                Missile.player_y -= Missile.SPEED
            if (Missile.player_y <= 0):
                Missile.reset_player() # gives player possibility to shoot again and resets missile
            
            for i in range(len(Enemy.enemies_x)):
                enemy_x = Enemy.enemies_x[i - 1]
                enemy_y = Enemy.enemies_y[i - 1] 
                if ((Missile.player_exist) & # colision detection player missile on enemy
                   (Missile.player_x + Missile.WIDTH >= enemy_x) & (Missile.player_x <= enemy_x + Enemy.SIZE) & # detect for x
                   (Missile.player_y <= enemy_y + Enemy.SIZE) & (Missile.player_y + Missile.HEIGHT >= enemy_y)): # detect for y
                   Enemy.enemies_x.pop(i - 1) # destroy enemy
                   Enemy.enemies_y.pop(i - 1)
                   Missile.reset_player() # reset player missile if hit enemy
                   Player.SCORE += 10 # adds 10 score
            if (len(Enemy.enemies_x) == 0): # initiate new wave of enemies
                Enemy.make()
                Player.LIVES += 1 # add player life

            if (Enemy.DIRECTION): # set movement direction: right
                Enemy.reset() # resets most left and most right
                for i in range(len(Enemy.enemies_x)): # checks for most right enemy
                    if (Enemy.enemies_x[i] >= Enemy.most_right):
                        Enemy.most_right = Enemy.enemies_x[i]
                if (Enemy.most_right + Enemy.SIZE < Base.WIDTH): # if not hit right border, move all to right
                    for i in range(len(Enemy.enemies_x)):
                        Enemy.enemies_x[i] += Enemy.SPEED
                else: # swtich direction if hit border
                    Enemy.DIRECTION = False
                    for i in range(len(Enemy.enemies_y)): #makes one leap down on border hit
                        Enemy.enemies_y[i] += Enemy.LEAP
            else:
                Enemy.reset()
                for i in range(len(Enemy.enemies_x)):
                    if (Enemy.enemies_x[i] <= Enemy.most_left): #checks for most left
                        Enemy.most_left = Enemy.enemies_x[i]
                if (Enemy.most_left > 0 ): # if not hit left border, move all to left
                    for i in range (len(Enemy.enemies_x)):
                        Enemy.enemies_x[i] -= Enemy.SPEED
                else:
                    Enemy.DIRECTION = True
                    for i in range(len(Enemy.enemies_y)):
                        Enemy.enemies_y[i] += Enemy.LEAP
            seconds = 1
            if (timer == seconds * Base.FPS): # enemy shoot every s seconds
                Missile.create_enemy()
                timer = 0


            for i in range(len(Bunker_Block.blocks_x)): # check colision between enemy missiles and bunker
                for j in range(len(Missile.enemy_missiles_x)):
                    if ((Missile.enemy_missiles_x[j - 1] + Missile.WIDTH >= Bunker_Block.blocks_x[i - 1]) & (Missile.enemy_missiles_x[j - 1] <= Bunker_Block.blocks_x[i - 1] + Bunker_Block.SIZE) &
                        (Missile.enemy_missiles_y[j - 1] + Missile.HEIGHT >= Bunker_Block.y) & (Missile.enemy_missiles_y[j - 1] <= Bunker_Block.y + Bunker_Block.SIZE)):
                        Bunker_Block.blocks_hp[i] -= 1
                        Missile.enemy_missiles_x.pop(j - 1)
                        Missile.enemy_missiles_y.pop(j - 1)
                        if (Bunker_Block.blocks_hp[i - 1] <= 0):
                            Bunker_Block.blocks_x.pop(i - 1)
                            Bunker_Block.blocks_hp.pop(i - 1)

            
            for i in range(len(Bunker_Block.blocks_x)): # checks colsion between player missile and bunker
                if ((Missile.player_exist) &
                    (Missile.player_x <= Bunker_Block.blocks_x[i - 1] + Bunker_Block.SIZE) & (Missile.player_x + Missile.WIDTH >= Bunker_Block.blocks_x[i - 1]) &
                    (Missile.player_y <= Bunker_Block.y + Bunker_Block.SIZE) & (Missile.player_y + Missile.HEIGHT >= Bunker_Block.y)):
                    Bunker_Block.blocks_hp[i - 1] -= 1
                    Missile.reset_player()
                    if (Bunker_Block.blocks_hp[i - 1] <= 0):
                        Bunker_Block.blocks_x.pop(i - 1)
                        Bunker_Block.blocks_hp.pop(i - 1)

            if (len(Missile.enemy_missiles_x) > 0):
                for i in range(len(Missile.enemy_missiles_x)):
                    if ((Missile.enemy_missiles_x[i - 1] + Missile.WIDTH >= Player.x) & (Missile.enemy_missiles_x[i - 1] <= Player.x + Player.WIDTH) & #enemy missile on player
                        (Missile.enemy_missiles_y[i - 1] + Missile.HEIGHT >= Player.y) & (Missile.enemy_missiles_y[i - 1] <= Player.y + Player.HEIGHT)):
                        Missile.enemy_missiles_x.pop(i - 1)
                        Missile.enemy_missiles_y.pop(i - 1)
                        if (not Player.sp_trigger): # -1 life if spawn protection timed out
                            Player.hit()

            if (len(Missile.enemy_missiles_x) > 0): 
                for i in range(len(Missile.enemy_missiles_y)):
                    if (Missile.enemy_missiles_y[i - 1] >= Base.HEIGHT - Enemy.SPEED): # clear missiles out of map
                        Missile.enemy_missiles_x.pop(i - 1)
                        Missile.enemy_missiles_y.pop(i - 1)

            if (Missile.player_exist): # check colision between player and enemy missile
                for i in range(len(Missile.enemy_missiles_x)):
                    if ((Missile.player_x + Missile.WIDTH >= Missile.enemy_missiles_x[i - 1]) & (Missile.player_x <= Missile.enemy_missiles_x[i - 1] + Missile.WIDTH) &
                        (Missile.player_y <= Missile.enemy_missiles_y[i - 1] + Missile.HEIGHT) & (Missile.player_y + Missile.HEIGHT >= Missile.enemy_missiles_y[i - 1])):
                        Missile.enemy_missiles_x.pop(i - 1)
                        Missile.enemy_missiles_y.pop(i - 1)
                        Missile.reset_player()


            if (len(Missile.enemy_missiles_x) > 0): 
                for i in range(len(Missile.enemy_missiles_y)):
                    Missile.enemy_missiles_y[i - 1] += Missile.enemy_SPEED # constantly move missiles down

            most_down = 0
            for i in range(len(Enemy.enemies_y)):
                if (Enemy.enemies_y[i] >= most_down):
                    most_down = Enemy.enemies_y[i]



            Base.draw()


    def draw():
        pygame.display.update()
        Base.clock.tick(Base.FPS)
        Base.screen.fill((0, 0, 0))
        font = pygame.font.SysFont('Arial', 15)
        score = font.render("Score: " + str(Player.SCORE) + "     Lives: " + str(Player.LIVES), True, (255, 255, 255))
        Base.screen.blit(score, (20, Base.HEIGHT - 30))
        if (Player.sp_trigger):
            invul = font.render("Invulnerable: Spawn Protection", True, (255,255,255))
            Base.screen.blit(invul, (200, Base.HEIGHT - 30))
        Player.draw()
        Missile.draw()
        Enemy.draw()
        Bunker_Block.draw()

    def over():
        while Base.GAME_OVER:
            for event in pygame.event.get():   #
                if event.type == pygame.QUIT:  # quit game
                    pygame.quit()              #
                    sys.exit()
            pygame.display.update()
            Base.clock.tick(Base.FPS)
            Base.screen.fill((0, 0, 0))
            font = pygame.font.SysFont('Arial', 36)
            over = font.render("Game over! Final score: " + str(Player.SCORE), True, (255, 255, 255))
            Base.screen.blit(over, (Base.WIDTH / 3, Base.HEIGHT / 2))

        




class Player:

    WIDTH = 20
    HEIGHT = 30
    SPEED = 5
    LIVES = 3
    SCORE = 0
    SPAWN_PROTECTION = 3
    sp_trigger = False
    x = Base.WIDTH / 2
    y = Base.HEIGHT - 75

    def hit():
        Player.LIVES -= 1
        Player.x = Base.WIDTH / 2
        Player.y = Base.HEIGHT - 75
        Player.spawn_protection = 3
        Player.sp_trigger = True
        Missile.reset_player()

    def draw():
        pygame.draw.rect(Base.screen,
                        (255, 255, 255),
                        pygame.Rect(Player.x, Player.y, Player.WIDTH, Player.HEIGHT))

class Missile:
    SPEED = 10
    WIDTH = 2
    HEIGHT = 4
    enemy_SPEED = 2
    enemy_missiles_x = []
    enemy_missiles_y = []
    player_exist = False
    player_x = Player.x + (Player.WIDTH / 2)
    player_y = Player.y - 5

    def reset_player():
        Missile.player_x = Player.x + (Player.WIDTH / 2)
        Missile.player_y = Player.y - 5
        Missile.player_exist = False

    def create_player(x):
        Missile.player_exist = True
        Missile.player_x = x + (Player.WIDTH / 2)

    def create_enemy():
        temp = []
        y = 0
        x = random.choice(Enemy.enemies_x)
        for i in range(len(Enemy.enemies_x)):
            if Enemy.enemies_x[i] == x:
                temp.append(i)
        for i in temp:
            if (Enemy.enemies_y[i] >= y):
                y = Enemy.enemies_y[i]
        Missile.enemy_missiles_x.append(x + Enemy.SIZE / 2)
        Missile.enemy_missiles_y.append(y + Enemy.LEAP + Enemy.SIZE)

        



    def draw():
        if (Missile.player_exist):
            pygame.draw.rect(Base.screen,
                            (0, 255, 0),
                            pygame.Rect(Missile.player_x, Missile.player_y, Missile.WIDTH, Missile.HEIGHT))
        if (len(Missile.enemy_missiles_x) > 0):
            for i in range(len(Missile.enemy_missiles_x)):
                pygame.draw.rect(Base.screen,
                            (175, 0, 0),
                            pygame.Rect(Missile.enemy_missiles_x[i], Missile.enemy_missiles_y[i], Missile.WIDTH, Missile.HEIGHT))



class Enemy:

    DISTANCE = 25
    SIZE = 30
    SPEED = 1
    DIRECTION = True
    LEAP = 3
    enemies_x = []
    enemies_y = []
    most_right = 0
    most_left = Base.WIDTH

    def reset():
        Enemy.most_right = 0
        Enemy.most_left = Base.WIDTH

    
    def make():
        for i in range(Enemy.DISTANCE, int(Base.HEIGHT / 3), Enemy.DISTANCE + Enemy.SIZE):
            for j in range(Enemy.DISTANCE, Base.WIDTH - (Enemy.DISTANCE + Enemy.SIZE), Enemy.DISTANCE + Enemy.SIZE):
                Enemy.enemies_x.append(j)
                Enemy.enemies_y.append(i)


    def draw():
        for i in range(len(Enemy.enemies_x)):
             pygame.draw.rect(Base.screen,
                                (255, 0, 0),
                                pygame.Rect(Enemy.enemies_x[i], Enemy.enemies_y[i], Enemy.SIZE, Enemy.SIZE))


class Bunker_Block:
    SIZE = int(Enemy.SIZE / 2)
    DISTANCE = int(SIZE * 4)
    HP = 10
    y = Player.y - 40
    blocks_x = []
    blocks_hp = []

    def make():
        for i in range(int(Bunker_Block.DISTANCE / 3), Base.WIDTH, (Bunker_Block.SIZE * 6) + Bunker_Block.DISTANCE):
            Bunker_Block.blocks_x.append(i + (Bunker_Block.SIZE * 0))
            Bunker_Block.blocks_hp.append(10)
            Bunker_Block.blocks_x.append(i + (Bunker_Block.SIZE * 1))
            Bunker_Block.blocks_hp.append(10)
            Bunker_Block.blocks_x.append(i + (Bunker_Block.SIZE * 2))
            Bunker_Block.blocks_hp.append(10)
            Bunker_Block.blocks_x.append(i + (Bunker_Block.SIZE * 3))
            Bunker_Block.blocks_hp.append(10)

    def draw():
        for i in range(len(Bunker_Block.blocks_x)):
             pygame.draw.rect(Base.screen,
                                (255, 255, 0),
                                pygame.Rect(Bunker_Block.blocks_x[i], Bunker_Block.y, Bunker_Block.SIZE, Bunker_Block.SIZE))



Base.main()