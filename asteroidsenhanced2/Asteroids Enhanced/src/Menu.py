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
import Game, Options


class MenuOption:

    def __init__(self, text, font, pos, command):

        self.text = text
        self.font = font
        self.pos = list(pos)
        ren = self.font.render(text, 1, (255, 255, 255))
        self.pos[0] -= ren.get_width()/2
        self.cmd = command
        self.selected = False

    def command(self):
        if self.cmd: self.cmd()

    def select(self):
        self.selected = True

    def deselect(self):
        self.selected = False

    def render(self, screen):
        if self.selected:
            ren = self.font.render(self.text, 1, (255, 255, 255))
        else:
            ren = self.font.render(self.text, 1, (175, 175, 175))
        screen.blit(ren, self.pos)


class Menu:

    def __init__(self, screen):
        self.versionID = "0.1.1 Alpha"
        self.screen = screen
        self.options = []
        self.font = load_font("nasaliza.ttf", 30)
        self.font2 = load_font("nasaliza.ttf", 70)
        self.font3 = load_font("nasaliza.ttf", 20)
        self.AddOption("New Arcade Game", self.runGame)
        self.AddOption("New Adventure Game (Disabled)", self.runAdventureGame)
        self.AddOption("Options", self.runOptions)
        self.AddOption("Quit Game", self.quitGame)
        self.options[0].select()
        self.option = 1
        self.all = Group()
        Asteroid.containers = self.all
        self.clock = pygame.time.Clock()
        load_sounds()
        play_menubg()
        for i in range(10):
            Asteroid(GeneratePos(), random.choice([0.5, 1.0, 1.25]))

    def runGame(self):
        game = Game.Game(self.screen)
        game.Run()

    def runOptions(self):
        options = Options.Options(self.screen, self.all)
        options.Run()
    
    def runAdventureGame(self):
        print "Running Adventure Game"
        
    def quitGame(self):
        pygame.quit()
        sys.exit()        

    def AddOption(self, text, command):
        pos = (320, 300 + len(self.options)*self.font.get_height())
        option = MenuOption(text, self.font, pos, command)
        self.options.append(option)

    def __moveDown(self):
        for o in self.options:
            o.selected = False
        self.option += 1
        if self.option > len(self.options):
            self.option = 1
        self.options[self.option-1].select()

    def __moveUp(self):
        for o in self.options:
            o.selected = False
        self.option -= 1
        if self.option < 0:
            self.option = len(self.options)-1
        self.options[self.option-1].select()

    def __menuInput(self):
        self.events = pygame.event.get()
        for e in self.events:
            if e.type == QUIT:
                pygame.quit()
                sys.exit()
            if e.type == KEYDOWN:
                if e.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if e.key == K_UP:
                    self.__moveUp()
                if e.key == K_DOWN:
                    self.__moveDown()
                if e.key == K_RETURN:
                    self.options[self.option-1].command()
            
    def __drawScene(self):
        self.screen.fill((0, 0, 0))
        self.all.draw(self.screen)
        for star in Stars():
            self.screen.set_at(star, (random.randint(0,255), random.randint(0,255), random.randint(0,255)))
        for o in self.options:
            o.render(self.screen)
        render_text(self.screen, "Asteroids Enchanced", self.font3, (320, 100), True)
        render_text(self.screen, "Copyright (C) 2008", self.font3, (320, 200), True)
        render_text(self.screen, "By Fusspawn", self.font3, (320, 225), True)
        render_text(self.screen, "Version: "+str(self.versionID), self.font3, (20,20), False)
        pygame.display.flip()

    def loop(self):
        
        while 1:
            self.clock.tick(60)
            self.all.update()
            self.__menuInput()
            self.__drawScene()

    def Run(self):
        self.loop()

