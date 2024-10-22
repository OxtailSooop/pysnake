import pygame
import random

import pygame.freetype

# TODO: Prevent walking backwards into your body
# TODO: Die when hit wall
# TODO: Main menu and scoring system
# TODO: tail

speed_multiplier = 10

WIDTH = 1280
HEIGHT = 720

TAIL_DISTANCE = 50

class Tail(pygame.sprite.Sprite):
    last_position = pygame.Vector2(0, 0)
    tail = None
    def __init__(self, last_position):
        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.image.load("./res/steve.png")
        self.image = pygame.transform.scale(self.image, (64, 64))
        
        self.rect = self.image.get_rect()
        self.rect.center = last_position

        self.last_position = pygame.Vector2(self.rect.center)
    def update(self, last_position):
        pygame.sprite.Sprite.update(self)

        self.last_position = self.rect.center

        self.rect.center = last_position

        if self.tail != None:
            self.tail.update(self.last_position)
    def add_tail(self, sprites):
        if self.tail == None:
            self.tail = Tail(self.last_position)
            sprites.add(self.tail)
        else:
            self.tail.add_tail(sprites)
    def remove_tail(self):
            if self.tail != None:
                self.tail.kill()
    def kill(self):
        pygame.sprite.Sprite.kill(self)
        self.remove_tail()
    
class Player(pygame.sprite.Sprite):
    last_position = pygame.Vector2(0, 0)
    tail = None
    direction = pygame.Vector2(0, 0)
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.image.load("./res/steve.png")
        self.image = pygame.transform.scale(self.image, (64, 64))

        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

        self.last_position = pygame.Vector2(self.rect.center)
    def update(self, keys):
        pygame.sprite.Sprite.update(self)

        self.last_position = self.rect.center

        if keys[pygame.K_UP] or keys[pygame.K_LEFT] or keys[pygame.K_DOWN] or keys[pygame.K_RIGHT]:
            self.direction = pygame.Vector2(0, 0)
            if keys[pygame.K_UP]:
                self.direction += (0, -1)
            elif keys[pygame.K_LEFT]:
                self.direction += (-1, 0)
            elif keys[pygame.K_DOWN]:
                self.direction += (0, 1)
            elif keys[pygame.K_RIGHT]:
                self.direction += (1, 0)

        self.rect.center += self.direction * speed_multiplier

        if self.tail != None:
            self.tail.update(self.last_position)
    def add_tail(self, sprites):
        if self.tail == None:
            self.tail = Tail(self.last_position)
            sprites.add(self.tail)
        else:
            self.tail.add_tail(sprites)
    def remove_tail(self):
        if self.tail != None:
            self.tail.kill()
    def kill(self):
        pygame.sprite.Sprite.kill(self)
        self.remove_tail()

class Apple(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        
        self.image = pygame.image.load("./res/apple.png")
        self.image = pygame.transform.scale(self.image, (64, 64))

        self.rect = self.image.get_rect()
        self.apple_rand()

    def apple_rand(self):
        self.rect.center = (random.randint(0, WIDTH), random.randint(0, HEIGHT))
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH

    def update(self):
        pygame.sprite.Sprite.update(self)

class State():
    GAMEPLAY = 0

class Game:
    background_image = None
    should_close = False
    state = State.GAMEPLAY
    clock = None
    display = None
    keys = None
    mouse_pos = pygame.Vector2(0, 0)
    sprites = None
    player = None
    apple = None
    font = None
    score = 0
    score_text = None
    dead = False
    highscore = 0

    def __init__(self):
        pygame.init()
        pygame.font.init()
        self.font = pygame.font.Font("./res/Peaberry-Font-v2.0/Peaberry Font Family/Peaberry Base/Peaberry-Base.otf", 30)
        self.background_image = pygame.image.load("./res/background.png")
        self.clock = pygame.time.Clock()
        self.display = pygame.display.set_mode((1280, 720), flags=pygame.SCALED)
        pygame.display.toggle_fullscreen()
        pygame.display.set_caption("steve (not snake)")
        pygame.display.set_icon(pygame.image.load("./res/icon.png"))
        self.keys = pygame.key.get_pressed()
        self.sprites = pygame.sprite.Group()
        self.player = Player(WIDTH / 2, HEIGHT / 2)
        self.apple = Apple()
        self.apple.apple_rand()
        # we want the player to render over the apple so the order is important
        self.sprites.add((self.apple, self.player))
        self.highscore = self.load_highscore()
        self.score_text = self.font.render("score: " + str(self.score), True, (0, 0, 0))
    def die(self):
        self.dead = True
        if self.score > self.highscore:
            open("highscore", "w").write(str(self.score))
            self.highscore = self.score
    def load_highscore(self):
        return int(open("highscore", "w+").read() or 0)
            
    def update(self):
        for event in pygame.event.get():
            match event.type:
                case pygame.WINDOWCLOSE | pygame.QUIT:
                    self.should_close = True
                    return
                case pygame.KEYDOWN | pygame.KEYUP: # only update keys if they are changed
                    self.keys = pygame.key.get_pressed()

        if not self.dead:
            self.player.update(self.keys)
            self.apple.update()

            if self.player.rect.colliderect(self.apple.rect):
                self.score += 1
                self.score_text = self.font.render("score: " + str(self.score), True, (0, 0, 0))
                self.apple.apple_rand()
                # self.player.add_tail(self.sprites)

            if self.player.rect.bottom > HEIGHT:
                self.die()
            if self.player.rect.top < 0:
                self.die()
            if self.player.rect.left < 0:
                self.die()
            if self.player.rect.right > WIDTH:
                self.die()
        else:
            if self.keys[pygame.K_SPACE]:
                self.dead = False
                self.score = 0
                self.score_text = self.font.render("score: " + str(self.score), True, (0, 0, 0))
                self.apple.apple_rand()
                self.player.kill()
                self.player = Player(WIDTH / 2, HEIGHT / 2)
                self.sprites.add(self.player)

        self.clock.tick(60)
    def draw(self):
        self.display.fill((255, 255, 255))
        self.display.blit(self.background_image, (0, 0))
        self.sprites.draw(self.display)
        if self.dead:
            dead_text = self.font.render("ur ded", False, (0, 0, 0))
            dead_text_rect = dead_text.get_rect(center=((WIDTH / 2), (HEIGHT / 2) - (dead_text.get_rect().height / 2)))
            self.display.blit(dead_text, dead_text_rect)

            score_text = self.font.render("score: " + str(self.score), False, (0, 0, 0))
            score_text_rect = score_text.get_rect(center=((WIDTH / 2), (HEIGHT / 2) - (score_text.get_rect().height / 2) + 25))
            self.display.blit(score_text, score_text_rect)

            highscore_text = self.font.render("highscore: " + str(self.highscore), False, (0, 0, 0))
            highscore_text_rect = highscore_text.get_rect(center=((WIDTH / 2), (HEIGHT / 2) - (highscore_text.get_rect().height / 2) + 50))
            self.display.blit(highscore_text, highscore_text_rect)

            space_cont = self.font.render("press space to continue", False, (0, 0, 0))
            space_cont_rect = space_cont.get_rect(center=((WIDTH / 2), (HEIGHT / 2) - (space_cont.get_rect().height / 2) + 75))
            self.display.blit(space_cont, space_cont_rect)
        else:
            self.display.blit(self.score_text, (0, 0))
                
        pygame.display.flip()
    def destroy(self):
        pygame.quit()
        exit(0)

if __name__ == "__main__":
    game = Game()

    while not game.should_close:
        game.update()
        game.draw()

    game.destroy()