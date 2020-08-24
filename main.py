import pygame
import math
import random
from pygame import Rect
from pygame import mixer
import sys


class QButton(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("quit.png")
        self.rect = self.image.get_rect()
        self.rect.left = 25
        self.rect.top = 490

    def update(self, *args):
        return 0

    def draw(self, display):
        display.blit(self.image, self.rect)


class RButton(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("reset.png")
        self.rect = self.image.get_rect()
        self.rect.left = 150
        self.rect.top = 490

    def update(self, *args):
        return 0

    def draw(self, display):
        display.blit(self.image, self.rect)


class Background(pygame.sprite.Sprite):
    def __init__(self, image_file, location):
        super().__init__()
        self.image = pygame.image.load(image_file)
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = location

    def update(self, *args):
        return 0

    def draw(self, display):
        display.blit(self.image, [0, 0])


class ShowPlane(pygame.sprite.Sprite):
    def __init__(self, speed):
        super().__init__()
        self.location = (800 + random.randint(10, 70), random.randint(50, 350))
        self.speed = speed
        self.image = pygame.image.load("jet2.png")
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = self.location

    def update(self, *args):
        self.rect.left -= int(self.speed)
        if self.rect.left <= -825:
            self.image=pygame.image.load("jet.png")
            self.speed = self.speed*-1
            self.rect.top = random.randint(50, 350)
        if self.rect.left >= 871:
            self.image=pygame.image.load("jet2.png")
            self.speed = self.speed*-1
            self.rect.top = random.randint(50, 350)

    def draw(self, display):
        display.blit(self.image, self.rect)


class Plane(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.location = (800 + random.randint(10, 1800), random.randint(50, 150))
        self.speed = random.randint(10, 30)/10
        self.image = pygame.image.load("smalljet.png")
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = self.location
        self.end_effect = mixer.Sound("game-over.wav")

    def update(self, *args):
        global player_health
        self.rect.left -= int(self.speed)
        if self.rect.left <= 0:
            player_health -= 1
            if player_health == 0:
                self.end_effect.play()
            self.rect.left = 800 + random.randint(20, 2000)

    def draw(self, display):
        display.blit(self.image, self.rect)


class Gun(pygame.sprite.Sprite):
    def __init__(self, image_file, location):
        super().__init__()
        self.location = location
        self.image = pygame.image.load(image_file)
        self.original_image = pygame.image.load(image_file)
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = location
        self.direction = pygame.Vector2(1, 0)
        self.bullets = pygame.sprite.Group()
        self.shoot = mixer.Sound("shoot.wav")

    def rotate(self):
        pos = pygame.mouse.get_pos()
        angle = 250 - math.atan2(pos[1] - self.location[0], pos[0] - self.location[1]) * 180 / math.pi
        self.image = pygame.transform.rotate(self.original_image, angle)
        self.rect = self.image.get_rect(center=(self.location[0], self.location[1]))

    def update(self, events):
        for e in events:
            if e.type == pygame.MOUSEBUTTONDOWN:
                self.bullets.add(Projectile())
                self.shoot.play()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_SPACE:
                    self.bullets.add(Projectile())
                    self.shoot.play()
        self.bullets.update()
        self.rotate()

    def draw(self, display):
        self.bullets.draw(display)
        display.blit(self.image, self.rect)


class Mouse(pygame.sprite.Sprite):
    def __init__(self, image_file):
        pygame.mouse.set_visible(False)
        super().__init__()
        self.image = pygame.image.load(image_file)
        self.rect = pygame.mouse.get_pos()

    def update(self, *args):
        self.rect = pygame.mouse.get_pos()

    def draw(self, display):
        display.blit(self.image, self.rect)


class Projectile(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("fire.png")
        self.rect = self.image.get_rect()
        self.target_x = pygame.mouse.get_pos()[0]
        self.target_y = pygame.mouse.get_pos()[1]
        self.pos = pygame.math.Vector2(410, 500)
        self.direction = pygame.math.Vector2(self.target_x, self.target_y) - self.pos
        self.direction = self.direction.normalize()
        self.velocity = 5
        self.pos += self.direction * 150
        self.rect = (self.pos[0] // 1, self.pos[1] // 1)

    def update(self):
        # Bounding box of the screen
        screen_r = pygame.display.get_surface().get_rect()
        # where we would move next
        next_pos = self.pos + self.direction * self.velocity
        self.pos = next_pos
        self.rect = (self.pos[0], self.pos[1])
        if not screen_r.contains(Rect(int(self.rect[0]), int(self.rect[1]), 24, 24)):
            return self.kill() # bullet missed

    def draw(self, display):
        display.blit(self.image, self.rect)


class Game(pygame.sprite.Sprite):
    def __init__(self):
        super(Game, self).__init__()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("AIR DEFENCE FORCES 2000")
        self.icon = pygame.image.load('bomb_icon.png')
        pygame.display.set_icon(self.icon)
        self.font = pygame.font.Font('freesansbold.ttf', 32)
        self.explosion = mixer.Sound("explosion.wav")
        self.BackGround = Background("background2.jpg", [0, 0])
        self.StartScreen = Background("start.png", [0, 0])
        self.EndScreen = Background("gameover.png", [0, 0])
        self.DefenceGun = Gun("gun3.png", [400, 500])
        self.first_Plane = ShowPlane(4)
        self.first_Plane.rect.left = 850
        self.mouse = Mouse("crosshair.png")
        self.reset = RButton()
        self.quit = QButton()
        self.running = True
        self.started = False
        self.sprites = pygame.sprite.Group()
        self.plane_Array = []
        for i in range(0, 10):
            self.plane_Array.append(Plane())
        self.start_screen_sprites = pygame.sprite.Group()
        self.end_screen_sprites = pygame.sprite.Group()
        self.start_screen_sprites.add(self.BackGround)
        self.start_screen_sprites.add(self.StartScreen)
        self.start_screen_sprites.add(self.mouse)
        self.start_screen_sprites.add(self.DefenceGun)
        self.start_screen_sprites.add(self.first_Plane)
        self.end_screen_sprites.add(self.BackGround)
        self.end_screen_sprites.add(self.EndScreen)
        self.end_screen_sprites.add(self.mouse)
        self.end_screen_sprites.add(self.DefenceGun)
        self.sprites.add(self.BackGround)
        self.sprites.add(self.mouse)
        for plane in self.plane_Array:
            self.sprites.add(plane)
        self.sprites.add(self.DefenceGun)

    def collision_detect(self):
        global player_score
        for plane in self.plane_Array:
            for bullet in self.DefenceGun.bullets:
                if plane.rect.colliderect(
                        Rect(int(bullet.rect[0]), int(bullet.rect[1]), 24, 24)):  # Rect(left, top, width, height)
                    player_score += 1
                    bullet.kill()
                    plane.rect.left = 800 + random.randint(20, 2000)
                    plane.speed += 0.3
                    self.explosion.play()

    def button_detect(self):
        global player_health
        global player_score
        m_pos = pygame.mouse.get_pos()
        if self.quit.rect.colliderect(Rect(int(m_pos[0]), int(m_pos[1]), 30, 30)):
            pygame.display.quit()
            pygame.quit()
            sys.exit()
        if self.reset.rect.colliderect(Rect(int(m_pos[0]), int(m_pos[1]), 30, 30)) and player_health == 0:
            player_score = 0
            player_health = 3
            self.started = False
            for plane in self.plane_Array:
                plane.speed = random.randint(10, 30)/10
                plane.rect.left = 800 + random.randint(20, 2000)

    def main(self):
        global player_health
        global player_score
        black = (0, 0, 0)
        clock = pygame.time.Clock()
        dt = 0
        mixer.music.load("eye_of_the_tiger_8_bit.mp3")
        mixer.music.set_volume(0.8)
        mixer.music.play(-1)
        events = pygame.event.get()
        self.start_screen_sprites.update(events)
        self.start_screen_sprites.draw(self.screen)
        self.DefenceGun.draw(self.screen)
        while True:
            events = pygame.event.get()
            text = self.font.render('Score: ' + str(player_score), True, black)
            text2 = self.font.render('Health: ' + str(player_health), True, black)
            textRect = text.get_rect()
            textRect2 = text2.get_rect()
            textRect.center = (650, 500)
            textRect2.center = (650, 530)
            if mixer.get_num_channels() > 1:
                mixer.music.set_volume(0.3)
            if mixer.get_num_channels() == 1:
                mixer.music.set_volume(0.8)
            for e in events:
                if e.type == pygame.QUIT:
                    return
                if e.type == pygame.MOUSEBUTTONDOWN:
                    self.button_detect()
                if e.type == pygame.KEYDOWN:
                    self.started = True
            if not self.started:
                self.start_screen_sprites.update(events)
                self.start_screen_sprites.draw(self.screen)
                self.DefenceGun.draw(self.screen)
            elif self.started and player_health > 0:
                self.sprites.update(events)
                self.collision_detect()
                self.sprites.draw(self.screen)
                self.DefenceGun.draw(self.screen)
            else:
                self.end_screen_sprites.update(events)
                self.end_screen_sprites.draw(self.screen)
                self.DefenceGun.draw(self.screen)
                self.screen.blit(self.reset.image, self.reset.rect)
            self.screen.blit(text, textRect)
            self.screen.blit(text2, textRect2)
            self.screen.blit(self.quit.image, self.quit.rect)
            pygame.display.update()
            dt = clock.tick(60)


pygame.init()
player_health = 3
player_score = 0
my_game = Game()
my_game.main()
