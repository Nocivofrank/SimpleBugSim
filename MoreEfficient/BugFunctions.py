import pygame, random

class Bug():
    bug_energy_cost = 10

    def __init__(self, pos, speed, attack, defense, mutation_chance, passive_eat, death_chance, reproduction_chance):
        #Position and direction attributes
        self.pos = pygame.Vector2(pos)
        self.vel = pygame.Vector2(0, 0)
        self.direction = pygame.Vector2(random.uniform(-1,1), random.uniform(-1,1)).normalize()

        #General Stats for bug
        self.color = "red"
        self.time_alive = 0
        self.times_split = 0
        self.dead = False

        #Bug Attributes
        self.speed = speed
        self.attack = attack
        self.defense = defense
        self.mutation_chance = mutation_chance
        self.passive_eat = passive_eat
        self.death_chance = death_chance
        self.reproduction_chance = reproduction_chance

        self.radius = Bug.bug_energy_cost
        self.max_radius = self.radius * 5
        self.attached_to = None

        