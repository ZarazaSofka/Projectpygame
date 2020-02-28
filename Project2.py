import pygame
import os
from random import choice, randrange
import sys

from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QPushButton
from PyQt5.QtCore import QRect
from PyQt5.QtGui import QPixmap


def game():
    pygame.init()
    size = width, height = 1000, 600
    screen = pygame.display.set_mode(size)
    ps = 0

    def text(scr, t, pos, col):
        scr.blit(pygame.font.Font(None, 20).render(t, 1, col), pos)

    def pause():
        fon = load_image('start.png')
        screen.blit(pygame.transform.scale(fon, (width, height)), (0, 0))

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game_over()
                elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                    return
            pygame.display.flip()
            clock.tick(10)

    def game_over():
        nonlocal ps
        fon = pygame.Surface((1000, 600))
        fon.fill((0, 0, 150))
        fon.blit(pygame.font.Font(None, 180).render('Result: ' + str(ps), 1, (0, 255, 255)),
                 (70, 50))
        fon.blit(pygame.font.Font(None, 100).render(
            'Records:', 1, (0, 255, 255)), (70, 210))
        ns = list(map(lambda a: int(a.strip()), open(os.path.join('data', 'rate.txt')).readlines()))
        ns.append(ps)
        ns.sort(reverse=True)
        ns = ns[:5]
        open(os.path.join('data', 'rate.txt'), 'w').writelines([str(e) + '\n' for e in ns])
        for i in range(5):
            fon.blit(pygame.font.Font(None, 90).render(
                f'{ns[i]}', 1, (0, 255, 255)), (70, 290 + 60 * i))
        screen.blit(pygame.transform.scale(fon, (width, height)), (0, 0))
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                    pygame.quit()
                    return
            pygame.display.flip()
            clock.tick(10)

    def fill(n):
        for i in range(n):
            n = (randrange(-10000, 10000), randrange(-10000, 10000))
            s = pygame.sprite.Sprite()
            s.rect = pygame.Rect(n[0], n[1], 100, 100)
            while pygame.sprite.spritecollideany(s, all_sprites):
                n = (randrange(-10000, 10000), randrange(-10000, 10000))
                s = pygame.sprite.Sprite()
                s.rect = pygame.Rect(n[0], n[1], 100, 100)
            o = randrange(14 - dif)
            if not o:
                def walls(t, pos):
                    nonlocal i
                    Wall((all_sprites, objects), n, t)
                    for j in range(4):
                        if not randrange(7):
                            s = pygame.sprite.Sprite()
                            s.rect = pygame.Rect(pos[0], pos[1], 50, 50)
                            s.rect.move([(-50, 0), (50, 0), (0, -50), (0, 50)][j])
                            if not pygame.sprite.spritecollideany(s, all_sprites):
                                i += 1
                                walls(t, s.rect.topleft)

                t = randrange(3)
                walls(t, n)
            elif 0 < o <= 7 - dif:
                Plant((all_sprites, objects), n)
            else:
                Animal((all_sprites, objects, animals), n)

    def load_image(name, colorkey=None):
        fullname = os.path.join('data', name)
        image = pygame.image.load(fullname).convert()
        if colorkey is not None:
            if colorkey == -1:
                colorkey = image.get_at((0, 0))
            image.set_colorkey(colorkey)
        else:
            image = image.convert_alpha()
        return image

    def turn(dx, dy):
        if dx < 0 and dy < 0:
            return 45
        if dx < 0 and dy == 0:
            return 90
        if dx < 0 < dy:
            return 135
        if dx > 0 and dy > 0:
            return -135
        if dx > 0 and dy == 0:
            return -90
        if dy < 0 < dx:
            return -45
        if dx == 0 and dy < 0:
            return 0
        if dx == 0 and dy == 0:
            return False
        if dx == 0 and dy > 0:
            return 180

    class Player(pygame.sprite.Sprite):
        stimage = load_image('slime.png', -1)
        actimage = load_image('slimemove.png', -1)
        image = stimage

        def __init__(self, g):
            super().__init__(g)
            self.rect = self.image.get_rect()
            self.rect.x = width // 2 - self.rect.w // 2
            self.rect.y = height // 2 - self.rect.h // 2
            self.mask = pygame.mask.from_surface(self.image)

            self.health = 100
            self.normal_speed = 10
            self.speed = 10
            self.defense = 0
            self.control = 0
            self.toxic = 0
            self.poison = 0
            self.immunity = 0
            self.get_immun = 0
            self.slow = 1
            self.skill = 5

        def move(self, dx=0, dy=0):
            if not dx and not dy:
                self.image = self.stimage
                if self.health // 2 > 200:
                    self.image = pygame.transform.scale(self.image, (200, 200))
                elif self.health // 2 >= 30:
                    self.image = pygame.transform.scale(self.image, (self.health // 2,
                                                                     self.health // 2))
                else:
                    self.image = pygame.transform.scale(self.image, (30, 30))
                self.rect = self.image.get_rect()
                self.rect.x = width // 2 - self.rect.w // 2
                self.rect.y = height // 2 - self.rect.h // 2
                self.mask = pygame.mask.from_surface(self.image)
                return
            dx, dy = dx * self.speed * 100 // self.health, dy * self.speed * 100 // self.health
            if dx < -50:
                dx = -50
            if dx > 50:
                dx = 50
            if dy < -50:
                dy = -50
            if dy > 50:
                dy = 50
            if self.control < 0:
                s = pygame.sprite.Sprite()
                if dx < 0 and dy < 0:
                    s.rect = (self.rect.x - 150, self.rect.y - 150, self.rect.x + 50,
                              self.rect.y + 50)
                elif dx > 0 > dy:
                    s.rect = (self.rect.x - 50, self.rect.y - 150, self.rect.x + 150,
                              self.rect.y + 50)
                elif dx < 0 < dy:
                    s.rect = (self.rect.x - 150, self.rect.y - 50, self.rect.x + 50,
                              self.rect.y + 150)
                elif dx > 0 and dy > 0:
                    s.rect = (self.rect.x - 50, self.rect.y - 50, self.rect.x + 150,
                              self.rect.y + 150)
                elif dx < 0:
                    s.rect = (self.rect.x - 150, self.rect.y - 100, self.rect.x + 50,
                              self.rect.y + 100)
                elif dx > 0:
                    s.rect = (self.rect.x - 50, self.rect.y - 100, self.rect.x + 150,
                              self.rect.y + 100)
                elif dy < 0:
                    s.rect = (self.rect.x - 100, self.rect.y - 150, self.rect.x + 100,
                              self.rect.y + 50)
                elif dy > 0:
                    s.rect = (self.rect.x - 100, self.rect.y - 50, self.rect.x + 100,
                              self.rect.y + 150)
                if pygame.sprite.spritecollideany(s, objects):
                    dx, dy = choice([(0, 0)] * (-self.control) + [(dx, dy)] * 10 +
                                    [(-dx // 2, - dy // 2)])
            elif self.control > 0:
                s = pygame.sprite.Sprite()
                if dx > 0 and dy > 0:
                    s.rect = (self.rect.x - 150, self.rect.y - 150, self.rect.x + 50,
                              self.rect.y + 50)
                elif dx < 0 < dy:
                    s.rect = (self.rect.x - 50, self.rect.y - 150, self.rect.x + 150,
                              self.rect.y + 50)
                elif dx > 0 > dy:
                    s.rect = (self.rect.x - 150, self.rect.y - 50, self.rect.x + 50,
                              self.rect.y + 150)
                elif dx < 0 and dy < 0:
                    s.rect = (self.rect.x - 50, self.rect.y - 50, self.rect.x + 150,
                              self.rect.y + 150)
                elif dx > 0:
                    s.rect = (self.rect.x - 150, self.rect.y - 100, self.rect.x + 50,
                              self.rect.y + 100)
                elif dx < 0:
                    s.rect = (self.rect.x - 50, self.rect.y - 100, self.rect.x + 150,
                              self.rect.y + 100)
                elif dy > 0:
                    s.rect = (self.rect.x - 100, self.rect.y - 150, self.rect.x + 100,
                              self.rect.y + 50)
                elif dy < 0:
                    s.rect = (self.rect.x - 100, self.rect.y - 50, self.rect.x + 100,
                              self.rect.y + 150)
                if pygame.sprite.spritecollideany(s, objects):
                    dx, dy = choice([(-dx, -dy)] * self.control +
                                    [(dx // 2, dy // 2)] * 10 + [(0, 0)])

            if self.health // 2 > 200:
                self.image = pygame.transform.scale(self.actimage, (200, 200))
            elif self.health // 2 >= 30:
                self.image = pygame.transform.scale(self.actimage,
                                                    (self.health // 2, self.health // 2))
            else:
                self.image = pygame.transform.scale(self.actimage, (30, 30))
            self.image = pygame.transform.rotate(self.image, turn(dx, dy))
            self.rect = self.image.get_rect()
            self.rect.x = width // 2 - self.rect.w // 2
            self.rect.y = height // 2 - self.rect.h // 2
            self.mask = pygame.mask.from_surface(self.image)

            self.rect.x += dx
            self.rect.y += dy
            if list(filter(lambda a: type(a) is Wall,
                           filter(lambda e: pygame.sprite.collide_mask(self, e), objects))) or \
                    not -20000 <= self.rect.x <= 20000 or not -20000 <= self.rect.y <= 20000:
                self.rect.x -= dx
                self.rect.y -= dy
            else:
                globcs[0] += dx
                globcs[1] += dy

        def update(self):
            nonlocal dif
            collided = list(filter(lambda e: pygame.sprite.collide_mask(self, e), objects))
            self.speed = self.normal_speed
            if self.toxic > 50:
                self.toxic = 50
            if self.health > 2000:
                dif = 4
            elif dif == 2 and self.health > 1000:
                dif = 3
            elif dif == 1 and self.health > 500:
                dif = 2
            elif dif == 0 and self.health > 250:
                dif = 1
            if collided:
                for o in collided:
                    if type(o) is not Wall:
                        if type(o) is Animal:
                            o.health -= (1 + self.health // 100)
                        else:
                            o.health -= (0.5 + self.health // 50)
                        if not randrange(10):
                            self.health += 1
                        if self.defense:
                            self.health -= choice([0] * self.defense + [o.attack] * 10)
                        else:
                            self.health -= o.attack
                        if self.toxic > o.poison and self.toxic > o.toxic:
                            o.poison = self.toxic
                        if o.toxic > self.poison and o.toxic > self.toxic:
                            self.poison = o.toxic
                        self.speed -= o.slow * self.speed // self.skill
                        if self.speed < 3:
                            self.speed = 3
            if self.poison:
                self.poisoned()
            if self.health <= 0:
                return False
            return True

        def poisoned(self):
            if self.poison >= 10 + self.immunity * 2 and not self.get_immun:
                self.get_immun = 5 + self.immunity
            elif self.get_immun:
                self.get_immun -= 1
                if not self.get_immun:
                    self.immunity += 1
            if self.immunity:
                self.health -= choice([0] * self.immunity + [1] * 10)
            else:
                self.health -= self.poison
            self.poison -= 1

    class Plant(pygame.sprite.Sprite):
        def __init__(self, g, pos):
            super().__init__(g)
            i = choice([[0, 0, 0, 0, 1, 1, 1, 2], [0, 0, 1, 1, 1, 1, 2, 2], [0, 1, 1, 2, 2, 2, 3, 3],
                        [1, 2, 2, 3, 3, 3, 4, 4], [1, 2, 3, 3, 4, 4, 4, 4]][dif])
            self.image = load_image('plant' + str(i) + '.png', -1)
            self.rect = self.image.get_rect()
            self.mask = pygame.mask.from_surface(self.image)
            self.pos = pos
            self.rect.x, self.rect.y = pos

            self.health, self.attack, self.slow, self.toxic = d[(type(self), i)]
            self.poison = 0

        def update(self):
            nonlocal ps
            self.rect.x = self.pos[0] - globcs[0]
            self.rect.y = self.pos[1] - globcs[1]
            if self.health != 1000:
                self.health += 0.2
            if self.poison:
                self.toxic = self.poison // 5
                self.poison = 0
            if self.health <= 0:
                if not randrange(10):
                    if self.attack == 0:
                        player.health += 20
                        if player.slow > 0:
                            player.slow -= 1
                        if player.control > 0:
                            player.control -= 1
                        elif player.control < 0:
                            player.control += 1
                    elif self.slow == 2:
                        player.health += 50
                    elif self.slow == 4:
                        player.slow += 1
                        player.health += 100
                    elif self.slow == 3:
                        player.health += 150
                        player.toxic += 1
                    else:
                        player.slow += 2
                        player.health += 300
                        self.toxic += 2
                if self.attack == 0:
                    ps += 10
                elif self.slow == 2:
                    ps += 20
                elif self.slow == 4:
                    ps += 30
                elif self.slow == 3:
                    ps += 40
                else:
                    ps += 60
                self.kill()

    class Animal(pygame.sprite.Sprite):
        def __init__(self, g, pos):
            super().__init__(g)
            i = choice([[0, 0, 0, 0, 1, 1, 1, 2], [0, 0, 1, 1, 1, 1, 2, 2], [0, 1, 1, 2, 2, 2, 3, 3],
                        [1, 2, 2, 3, 3, 3, 4, 4], [2, 3, 3, 4, 4, 4, 5, 5]][dif])
            self.origimage = load_image('animal' + str(i) + '.png', -1)
            self.image = self.origimage
            self.rect = self.image.get_rect()
            self.mask = pygame.mask.from_surface(self.image)
            self.pos = pos
            self.rect.x, self.rect.y = pos

            self.health, self.attack, self.normal_speed, self.slow, self.toxic, self.control =\
                d[(type(self), i)]
            self.speed = self.normal_speed
            self.poison = 0

            self.predx, self.predy = 0, 0

        def move(self):
            self.predx, self.predy = choice([self.predx for _ in range(20)] + [randrange(-1, 2)]), \
                                     choice([self.predy for _ in range(20)] + [randrange(-1, 2)])
            dx, dy = self.predx * self.speed, self.predy * self.speed
            if not dx and not dy:
                return
            if self.control < 0:
                s = pygame.sprite.Sprite()
                if dx < 0 and dy < 0:
                    s.rect = pygame.Rect(self.rect.x - 150, self.rect.y - 150, 150, 150)
                elif dx > 0 > dy:
                    s.rect = pygame.Rect(self.rect.x, self.rect.y - 150, 150, 150)
                elif dx < 0 < dy:
                    s.rect = pygame.Rect(self.rect.x - 150, self.rect.y, 150, 150)
                elif dx > 0 and dy > 0:
                    s.rect = pygame.Rect(self.rect.x, self.rect.y, 150, 150)
                elif dx < 0:
                    s.rect = pygame.Rect(self.rect.x - 150, self.rect.y - 100, 150, 200)
                elif dx > 0:
                    s.rect = pygame.Rect(self.rect.x, self.rect.y - 100, 150, 200)
                elif dy < 0:
                    s.rect = pygame.Rect(self.rect.x - 100, self.rect.y - 150, 200, 150)
                elif dy > 0:
                    s.rect = pygame.Rect(self.rect.x - 100, self.rect.y - 50, 200, 150)
                if pygame.sprite.spritecollideany(s, pl):
                    dx, dy = -dx, -dy
            elif self.control > 0:
                if pygame.sprite.collide_mask(self, player):
                    dx, dy = self.predx, self.predy
                else:
                    s = pygame.sprite.Sprite()
                    if dx > 0 and dy > 0:
                        s.rect = pygame.Rect(self.rect.x - 100, self.rect.y - 100, 100, 100)
                    elif dx < 0 < dy:
                        s.rect = pygame.Rect(self.rect.x, self.rect.y - 100, 100, 100)
                    elif dx > 0 > dy:
                        s.rect = pygame.Rect(self.rect.x - 100, self.rect.y, 100, 100)
                    elif dx < 0 and dy < 0:
                        s.rect = pygame.Rect(self.rect.x, self.rect.y, 100, 100)
                    elif dx > 0:
                        s.rect = pygame.Rect(self.rect.x - 150, self.rect.y - 50, 150, 100)
                    elif dx < 0:
                        s.rect = pygame.Rect(self.rect.x, self.rect.y - 50, 150, 100)
                    elif dy > 0:
                        s.rect = pygame.Rect(self.rect.x - 50, self.rect.y - 150, 100, 150)
                    elif dy < 0:
                        s.rect = pygame.Rect(self.rect.x - 50, self.rect.y, 100, 150)
                    if pygame.sprite.spritecollideany(s, pl):
                        dx, dy = choice([(-dx, -dy)] * self.control +
                                        [(dx // 2, dy // 2)] * 10 + [(0, 0)])

            self.image = pygame.transform.rotate(self.origimage, turn(dx, dy))
            self.rect = self.image.get_rect()
            self.rect.x = self.pos[0] - globcs[0]
            self.rect.y = self.pos[1] - globcs[1]
            self.mask = pygame.mask.from_surface(self.image)

            self.rect.x += dx
            self.rect.y += dy
            if list(filter(lambda a: type(a) is Wall,
                           filter(lambda e: pygame.sprite.collide_mask(self, e), objects))):
                self.predx, self.predy = -self.predx, self.predy
            elif -20000 <= self.rect.x <= 20000 and -20000 <= self.rect.y <= 20000:
                self.pos = (self.pos[0] + dx, self.pos[1] + dy)
            self.rect.x -= dx
            self.rect.y -= dy

        def update(self):
            nonlocal ps
            self.rect.x = self.pos[0] - globcs[0]
            self.rect.y = self.pos[1] - globcs[1]
            if pygame.sprite.collide_mask(self, player):
                self.speed -= player.slow
            else:
                self.speed = self.normal_speed
            if self.poison:
                self.health -= self.poison
                self.poison -= 1
            if self.health <= 0:
                if not randrange(10):
                    if self.normal_speed == 9:
                        player.normal_speed += 1
                        player.control -= 1
                    elif self.toxic:
                        player.toxic += 2
                        if player.control > 0:
                            player.control -= 1
                        elif player.control < 0:
                            player.control += 1
                    elif self.normal_speed == 7:
                        player.control += 1
                        player.health += 100
                    elif self.control == -3:
                        player.health += 150
                        if player.toxic > 0:
                            player.toxic -= 1
                    elif self.normal_speed == 8:
                        player.normal_speed += 1
                        player.control += 2
                        player.health += 200
                    else:
                        if player.normal_speed > 4:
                            player.normal_speed -= 1
                        player.health += 300
                if self.normal_speed == 9:
                    ps += 10
                elif self.toxic:
                    ps += 60
                elif self.normal_speed == 7:
                    ps += 20
                elif self.control == -3:
                    ps += 30
                elif self.normal_speed == 8:
                    ps += 70
                else:
                    ps += 40
                self.kill()

    class Wall(pygame.sprite.Sprite):
        def __init__(self, g, pos, i):
            super().__init__(g)
            self.image = load_image('wall' + str(i) + '.png')
            self.rect = self.image.get_rect()
            self.mask = pygame.mask.from_surface(self.image)
            self.pos = pos
            self.rect.x, self.rect.y = pos

        def update(self):
            self.rect.x = self.pos[0] - globcs[0]
            self.rect.y = self.pos[1] - globcs[1]

    d = {(Animal, 0): [60, 0, 9, 0, 0, -10], (Animal, 1): [150, 1, 7, 1, 0, 5],
         (Animal, 2): [250, 2, 6, 1, 0, -3], (Animal, 3): [500, 3, 6, 2, 0, 3],
         (Animal, 4): [400, 5, 8, 1, 0, 10], (Animal, 5): [200, 4, 7, 1, 10, 2],
         (Plant, 0): [40, 0, 1, 0], (Plant, 1): [100, 1, 2, 0], (Plant, 2): [150, 2, 4, 0],
         (Plant, 3): [250, 2, 3, 3], (Plant, 4): [400, 1, 5, 10]}

    all_sprites = pygame.sprite.Group()
    objects = pygame.sprite.Group()
    animals = pygame.sprite.Group()
    pl = pygame.sprite.GroupSingle()
    player = Player((all_sprites, pl))

    globcs = [0, 0]
    dif = 0
    clock = pygame.time.Clock()
    running = True
    pause()
    while running:
        if len(objects.spritedict) < (40 + 5 * dif) ** 2 // 2:
            screen.blit(pygame.transform.scale(load_image('clouds.png', -1),
                                               (width, height)), (0, 0))
            pygame.display.flip()
            fill((40 + 5 * dif) ** 2 - len(objects.spritedict))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        if not running:
            break
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            pause()
        dx, dy = 0, 0
        if keys[pygame.K_RIGHT]:
            dx = 1
        if keys[pygame.K_LEFT]:
            dx += -1
        if keys[pygame.K_UP]:
            dy = -1
        if keys[pygame.K_DOWN]:
            dy += 1
        for e in animals.spritedict.keys():
            if -1000 < e.rect.x < 1000 and -1000 < e.rect.y < 1000:
                e.move()
        player.move(dx, dy)
        running = player.update()
        if not running:
            player.kill()
            break
        objects.update()
        screen.fill((0, 100, 0))
        objects.draw(screen)
        pl.draw(screen)
        text(screen, 'HEALTH: ' + str(player.health), (5, 10), (255, 255, 255))
        text(screen, 'DEFENSE: ' + str(player.defense), (5, 40), (255, 255, 255))
        text(screen, 'IMMUNITY: ' + str(player.immunity), (5, 70), (255, 255, 255))
        text(screen, 'SPEED: ' + str(player.speed), (5, 100), (255, 255, 255))
        if player.control < 0:
            text(screen, 'CONTROL: COWARDICE', (5, 130), (255, 255, 255))
        elif player.control > 0:
            text(screen, 'CONTROL: BLOODTHIRSTINESS', (5, 130), (255, 255, 255))
        else:
            text(screen, 'CONTROL: NORMAL', (5, 130), (255, 255, 255))
        text(screen, 'TOXICITY: ' + str(player.toxic), (5, 160), (255, 255, 255))
        text(screen, 'X: ' + str(globcs[0]), (5, 190), (255, 255, 255))
        text(screen, 'Y: ' + str(globcs[1]), (5, 220), (255, 255, 255))
        text(screen, 'POINTS: ' + str(ps), (5, 270), (200, 200, 255))
        text(screen, 'DIFFICULTY: ' + str(dif + 1), (5, 300), (200, 200, 255))
        collided = list(filter(lambda e: pygame.sprite.collide_mask(player, e), objects))
        for e in collided:
            if type(e) is not Wall:
                text(screen, str(int(e.health)), (e.rect.x, e.rect.y - 10), (255, 0, 0))
        clock.tick(3)
        pygame.display.flip()
    game_over()


def start():
    class MainWidget(QWidget):
        def __init__(self):
            super().__init__()
            self.setGeometry(500, 180, 300, 450)
            self.setFixedSize(300, 450)
            self.setWindowTitle('Adventure')
            self.setStyleSheet("background-color: rgb(0, 80, 180)")

            self.name = QLabel(self)
            self.name.setObjectName("name")
            p = QPixmap(os.path.join('data', 'name.png'))
            self.name.setGeometry(QRect(50, 10, p.width(), p.height()))
            self.name.setPixmap(p)

            self.rate = QLabel(self)
            self.rate.setGeometry(QRect(50, 150, 200, 300))
            self.rate.setStyleSheet("color: yellow; font: bold 14px")
            self.rate.setText('Records:\n\n' + '\n'.join(open(os.path.join('data',
                                                                           'rate.txt')).readlines()))
            self.pushButton = QPushButton(self)
            self.pushButton.setGeometry(QRect(90, 110, 120, 40))
            self.pushButton.setObjectName("start")
            self.pushButton.setStyleSheet(
                """background-color: rgb(224, 0, 0); color: yellow; 
            border-radius: 4px; border: 2px solid rgb(150, 10, 10); font: bold 14px"""
            )
            self.pushButton.setText('Start')

            self.pushButton.clicked.connect(game)

    app = QApplication(sys.argv)
    ex = MainWidget()
    ex.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    start()
