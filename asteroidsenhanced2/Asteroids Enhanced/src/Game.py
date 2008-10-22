#! /usr/bin/env python

# Asteroids Enhanced - A arcade space shooter programmed by Fusspawn
# Copyright (C) 2008  Fusspawn
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA


import sys, os
import math, random


import pygame
from pygame.locals import *

from Engine import *
from GameObjects import *
from Menu import *

USE_ANTIALIAS = True


class Game:

    def __init__(self, screen):

        self.screen = screen
        self.sprites = Group()
        self.clearables = Group()
        self.asteroids = Group()
        self.ufos = Group()
        self.shots = Group()
        self.enemyshots = Group()
        self.particles = Group()
        self.missiles = Group()
        self.aoe = Group()
        self.Missile = 5
        self.nuke = 1
        self.ShockWaves = 2
        self.Shield = 5
        self.BG1 = pygame.image.load('./data/bg1.png').convert()
        self.BG2 = pygame.image.load('./data/bg2.png').convert()
        self.BackGround = self.BG1
        self.bgID = 1
        self.levelstart = 0
        self.DeathMessage = 0

        Ship.containers = self.sprites
        Shot.containers = self.sprites, self.shots, self.clearables
        Missile.containers = self.sprites, self.shots, self.clearables
        EnemyShot.containers = self.sprites, self.enemyshots, self.clearables
        Asteroid.containers = self.sprites, self.asteroids, self.clearables
        Ufo.containers = self.sprites, self.ufos, self.clearables
        Exhaust.containers = self.sprites, self.particles
        Particle.containers = self.sprites, self.particles
        Shockwave.containers = self.sprites, self.particles, self.aoe

        self.ship = Ship()
        Asteroid(GeneratePos())
        self.paused = False

        self.clock = pygame.time.Clock()
        self.events = []

        self.level = 1
        self.score = 0
        self.lives = 5
        self.done = False
        self.highscore = load_highscore()

        self.font = load_font("nasaliza.ttf", 20)
        self.font2 = load_font("nasaliza.ttf", 60)
        self.font3 = load_font("nasaliza.ttf", 30)
        load_sounds()
        play_bg()

    def __clearSprites(self):
        for s in self.clearables:
            pygame.sprite.Sprite.kill(s)
        
    def __collisionDetect(self):

        for a in self.asteroids:
            for s in self.shots:
                if Collision(a.drawpoints, s.drawpoints):
                    a.hit()
                    s.kill()
                    play_boom()
                    self.score += 75*a.scale
            for p in self.aoe:
                if Collision(a.drawpoints, p.points):
                    a.hit()
                    p.kill()
                    self.score += 75*a.scale

        for a in self.asteroids:
            if Collision(a.drawpoints, self.ship.drawpoints):
                if self.ship.alive() and self.Shield == 0:
                    self.ship.kill()
                    play_boom()
                    self.lives -= 1
                    self.__clearSprites()
                    self.DeathMessage = 1
                elif self.ship.alive() and self.Shield > 0:
                    a.kill()
                    self.Shield -= 1
                    play_boom()
                    


        for s in self.enemyshots:
            if Collision(s.drawpoints, self.ship.drawpoints):
                if self.ship.alive() and self.Shield == 0:
                    self.ship.kill()
                    play_boom()
                    self.lives -= 1
                    self.__clearSprites()
                    self.Shield = 3
                    self.DeathMessage = 1
                elif self.ship.alive() and self.Shield > 0:
                    self.Shield -= 1
                    play_boom()

        for u in self.ufos:
            for s in self.shots:
                if Collision(u.drawpoints, s.drawpoints):
                    s.kill()
                    u.kill()
                    self.score += 125
                    play_boom()
                    if self.nuke < 5:
                        self.nuke += 1
            


    def __drawScene(self):
        self.screen.fill((0, 0, 0))
        self.screen.blit(self.BackGround,(0,0))
        for star in Stars():
            self.screen.set_at(star, (random.randint(0,255), random.randint(0,255), random.randint(0,255)))
        self.sprites.draw(self.screen)
        render_text(self.screen, "Score: %06d" % self.score, self.font, (10, 10))
        render_text(self.screen, "High: %06d" % self.highscore, self.font, (260, 10))
        render_text(self.screen, "Level: %d" % self.level, self.font, (500, 10))
        render_text(self.screen, "Missiles: "+str(self.Missile),self.font,(500, 30))
        render_text(self.screen, "Nukes: "+str(self.nuke),self.font,(500,50))
        render_text(self.screen, "Shock's: "+str(self.ShockWaves),self.font,(500,70))
        if self.Shield > 2:
            render_text(self.screen, "Sheild:"+str((self.Shield*20))+" %",self.font,(510,460))
        else:
            render_text(self.screen, "Sheild:"+str((self.Shield*20))+" %",self.font,(510,460),False ,(255,0,0))
        for i in range(self.lives):
            LifeImage(self.screen, (20 + i*20, 50))
        if self.lives <= 0 and not self.particles:
            render_text(self.screen, "Game Over!", self.font2, (320, 225), True)
            render_text(self.screen, "Press Escape to Exit", self.font3, (320, 270), True)
        self.__renderMessages()
        pygame.display.flip()

    def __gameInput(self):
        self.events = pygame.event.get()
        for e in self.events:
            if e.type == QUIT:
                pygame.quit()
                sys.exit()
            if e.type == KEYDOWN:
                if e.key == K_ESCAPE:
                    self.done = True
                if e.key == K_a:
                    global USE_ANTIALIAS
                    USE_ANTIALIAS ^= 1
                if e.key == K_p:
                    self.paused ^= 1
            if e.type == ACTIVEEVENT:
                if (e.state == 2 and e.gain == 0) or (e.state == 6 and e.gain == 0):
                    self.paused = True
                elif e.state == 6 and e.gain == 1:
                    self.paused = False
                    
                    
    def __renderMessages(self):
        if self.levelstart > 0 and self.levelstart < 150 and self.DeathMessage == 0:
            self.levelstart += 1
            render_text(self.screen,"Level: "+str(self.level),self.font3,(320,240),True)
            if self.levelstart == 150:
                self.levelstart = 0
        if self.DeathMessage > 0 and self.DeathMessage < 100:
            self.DeathMessage += 1
            render_text(self.screen,"You Died!",self.font3,(320,240),True)
            if self.DeathMessage == 100:
                self.DeathMessage = 0
                                    
            
    def __playerInput(self):
        for e in self.events:
            if e.type == KEYDOWN:
                if e.key in (K_z, K_LCTRL, K_SPACE) and self.ship.alive():
                    Shot(self.ship.pos, self.ship.angle)
                    play_shoot()
                    
                if e.key in (K_m, K_RCTRL) and self.ship.alive() and self.Missile > 0:
                    Missile(self.ship.pos, self.ship.angle)
                    self.Missile -= 1
                    play_shoot()
                    
                if e.key == K_b and self.ship.alive() and self.ShockWaves > 0:
                    self.ShockWaves -= 1
                    for i in range(20):
                        Shockwave(self.ship.pos)
                        play_boom()
                    
                if e.key == K_n:
                    if self.nuke > 0:
                        self.nuke -= 1
                        play_boom()
                        for a in self.asteroids:
                            a.kill()
                        for u in self.ufos:
                            u.kill()
                    
                    
                if e.key in (K_x, K_LALT, K_RALT):
                    if self.ship.warp_timer <= 0:
                        points = []
                        for y in range(15):
                            for x in range(20):
                                points.append([x*32, y*32])
                        for a in self.asteroids:
                            for p in points:
                                if PointCollision(a, p):
                                    points.remove(p)
                        self.ship.pos = list(random.choice(points))
                        self.ship.velocity = [0, 0]
                        self.ship.warp_timer = 200

    def __updateGame(self):
        for s in self.sprites:
            s.use_antialias = USE_ANTIALIAS
        if not self.ship.alive() and not self.particles and self.lives > 0:
            self.ship = Ship()
            self.levelstart = 1
            for i in range(self.level):
                Asteroid(GeneratePos())
        
        if not self.asteroids and self.ship.alive():
            self.__clearSprites()
            self.level += 1
            self.levelstart = 1
            self.Missile = (5 + self.level)
            self.ShockWaves += 1
            self.ship.pos = [320, 240]
            self.ship.velocity = [0, 0]
            for i in range(self.level):
                Asteroid(GeneratePos())
            if self.Shield < 5:
                self.Shield += 1
            if self.bgID == 1:
                self.BackGround = self.BG2
                self.bgID = 2
            elif self.bgID == 2:
                self.BackGround = self.BG1
                self.bgID = 1

        if self.score > self.highscore:
            self.highscore = self.score
            save_highscore(int(self.highscore))

        for u in self.ufos:
            if not random.randrange(30) and self.ship.alive():
                EnemyShot(u.pos, AngleToTarget(u.pos, self.ship.pos))
                play_ufo()
        if not random.randrange(950) and not self.ufos and self.ship.alive():
            Ufo()

    def __mainLoop(self):
        
        while not self.done:

            self.clock.tick(60)
            self.sprites.update()

            while self.paused: self.__gameInput()
            self.__gameInput()
            self.__playerInput()
            self.__collisionDetect()
            self.__updateGame()
            self.__drawScene()
            

    def Run(self):
        self.__mainLoop()
