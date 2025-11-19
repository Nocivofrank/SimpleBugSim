import pygame, secrets
import numpy as np
import brain as Brain

class Bug():
    bug_energy_cost = 10
    bug_energy_decay = .01

    max_ranges = {
        "speed": [0 , 10.0],
        "attack": [0 , 1.0],
        "defense": [0 , 1.0],
        "mutation": [0 , 1.0],
        "accuracy": [0, 1.0],
        "passive eat": [0 , .5],
        "death": [0 , 1.0],
        "reproduction": [0 , 1.0],
        "size": [0 , 100],
        "color": [0 , 255],
        "canibal": False
    }

    change_interval_range = [ 0 , 10 ]

    universe_energy = None

    screenWidth = 0
    screenHeight = 0

    mouse_pos = pygame.Vector2(0 , 0)
    scroll_wheel_range = 0

    #brian row and columns
    input_size = 12
    hidden_size = 10
    output_size = 4

    bugs = []

    def __init__(self, pos, posGrid, color, speed, attack, defense, mutation_chance, accuracy, passive_eat, death_chance, reproduction_chance, canibal, brain):
        #Position and direction attributes
        self.pos = pygame.Vector2(pos)
        self.pos_grid = posGrid
        self.vel = pygame.Vector2(0, 0)
        self.direction = pygame.Vector2(0 , 0)
        self.image = self.make_surface(Bug.bug_energy_cost, color)
        self.draw_stat = False

        self.brain = brain

        #General Stats for bug
        self.color = color
        self.time_alive = 0
        self.change_timer = 0
        self.change_interval = 0
        self.times_split = 0
        self.amount_near = 1
        self.amount_relative_near = 0
        self.dead = False

        #brain actions
        self.do_attack = False
        self.do_breed = False
        self.do_breed_other = False

        #Bug Attributes
        self.speed = speed
        self.attack = attack
        self.defense = defense
        self.mutation_chance = mutation_chance
        self.accuracy = accuracy
        self.passive_eat = passive_eat
        self.death_chance = death_chance
        self.reproduction_chance = reproduction_chance
        self.canibal = canibal

        self.radius = Bug.bug_energy_cost
        self.max_radius = Bug.max_ranges["size"][1]
        self.attached_to = None
        self.attached_bug_dist = 0

        #Text initalizations
        self.bug_age = None
        self.bug_stat_text = None
        self.bug_stat_text_1 = None

        Bug._mutate(self)
        self.brain.brainMutate()

    def _update(self, dt, screen, UE, bugs):
        Bug.universe_energy = UE
        Bug.bugs=bugs
        Bug.screenWidth = screen.get_width()
        Bug.screenHeight = screen.get_height()

        if not self.dead:
            #Bug energy decay
            if Bug.mouse_pos.distance_to(self.pos) > 25:
                if (self.radius >= 1):
                    UE[0] += self.radius * dt * Bug.bug_energy_decay
                    self.radius -= self.radius * dt * Bug.bug_energy_decay  # size tax
                else:
                    self.dead = True
                    UE[0] += self.radius
                    return

            #Runs timer that moves bug at set intervals
            self.change_timer += dt
            if self.change_timer >= self.change_interval:
                Bug.thinkFoward(self)
                self.change_timer = 0
                self.change_interval = Bug.random_range(Bug.change_interval_range[0], Bug.change_interval_range[1])

            #gives bugs movement
            effective_radius = max(self.radius, 10)
            if self.direction.length() != 0:
                self.direction = self.direction.normalize()
            self.vel += self.direction * (self.speed / effective_radius * 20) * dt
            self.vel *= 0.85
            self.pos += self.vel * dt

            #wrap around edges
            if self.pos.x < -self.radius:
                self.pos.x = screen.get_width() + self.radius
            elif self.pos.x > screen.get_width() + self.radius:
                self.pos.x = -self.radius

            if self.pos.y < -self.radius:
                self.pos.y = screen.get_height() + self.radius
            elif self.pos.y > screen.get_height() + self.radius:
                self.pos.y = -self.radius

        bugs = Bug.bugs
        UE = Bug.universe_energy
        # Bug._update_pos_to_grid(self)
        # Bug._detect_near(self,screen,dt)
        Bug._reproduce(self)
    
    def _draw(self, screen, font):
        pygame.draw.circle(screen, self.color, self.pos, self.radius)
        # pygame.draw.rect(screen, self.color, (self.pos.x, self.pos.y, self.radius, self.radius))
        if font:
            bug_amount = 0
            if self.attached_to != None:
                bug_amount = len(self.attached_to)
            # if self.draw_stat:
            #     self.bug_age = font.render(f"Age: {self.time_alive}", True, (255, 255, 255))
            #     self.bug_stat_text = font.render(f"Atk: {self.attack:.2f} , Def: {self.defense:.2f}, Size: {self.radius:.2f}", True, (255,255,255))
            #     self.bug_stat_text_1 = font.render(f"PasEat: {self.passive_eat:.2f} , Split: {self.times_split}, MutCha: {self.mutation_chance:.2f}", True, (255,255,255))
            #     # self.bug_grid_pos_text = font.render(f"Grid Pos: {self.pos_grid} , Bugs near: {bug_amount}", True, (255,255,255))

            #     screen.blit(self.bug_age, (self.pos.x , self.pos.y + 10))
            #     # screen.blit(self.bug_grid_pos_text, (self.pos.x , self.pos.y - 20))
            #     if not self.dead:
            #         screen.blit(self.bug_stat_text, (self.pos.x , self.pos.y))
            #         screen.blit(self.bug_stat_text_1, (self.pos.x , self.pos.y - 10))

    def _mutate(self):
        def maybe_mutate(value, min_val, max_val, intensity=0.2):
            if Bug.random_range(0,1) <= self.mutation_chance:
                delta = Bug.random_range(-intensity, intensity)
                new_value = value + delta
                if new_value <= 0:
                    return 0
                return new_value
            return value

        #This is where i apply the mutations
        self.attack              = maybe_mutate(self.attack,              Bug.max_ranges["attack"][0],       Bug.max_ranges["attack"][1])
        self.defense             = maybe_mutate(self.defense,             Bug.max_ranges["defense"][0],      Bug.max_ranges["defense"][1])
        self.mutation_chance     = maybe_mutate(self.mutation_chance,     Bug.max_ranges["mutation"][0],     Bug.max_ranges["mutation"][1])
        self.change_interval     = maybe_mutate(self.change_interval,     Bug.change_interval_range[0],      Bug.change_interval_range[1])
        self.passive_eat         = maybe_mutate(self.passive_eat,         Bug.max_ranges["passive eat"][0],  Bug.max_ranges["passive eat"][1])
        self.death_chance        = maybe_mutate(self.death_chance,        Bug.max_ranges["death"][0],        Bug.max_ranges["death"][1])
        self.reproduction_chance = maybe_mutate(self.reproduction_chance, Bug.max_ranges["reproduction"][0], Bug.max_ranges["reproduction"][1])

        Bug.update_surface(self)

    def _reproduce(self):
        if not self.dead and self.radius > Bug.bug_energy_cost * 2:
            if Bug.random_range(0 , 1.0) <= self.reproduction_chance / self.amount_near:
                if self.radius >= Bug.bug_energy_cost:
                    #creates a new bug
                    Bug._create_bug(self, (self.pos.x + Bug.random_range(-self.radius * 2, self.radius * 2), self.pos.y + Bug.random_range(-self.radius * 2 , self.radius * 2)), self.brain )
                    self._grow_single(-Bug.bug_energy_cost)
                    self.times_split += 1

                    Bug.update_surface(self)

    def _grow_single(self, amount):
        self.radius += amount
        self.update_surface()

    def _grow(self, amount, other_bug):
        # Growth depends on relative size
        ratio = (other_bug.radius + amount) / max(self.radius, 0.0001)

        # Growth scaling (tweakable)
        growth = ratio * 0.2   # smaller ants grow fast / big ants grow slow

        # Apply growth but cap it
        growth = min(growth, 0.2)

        self.radius += growth
        self.update_surface()

    def _age(self):
        self.time_alive += 1
    
    def _detect_near(self, screen, dt):
        if not self.dead:
            # Check interactions with other bugs
            for other_bug in Bug.bugs:
                self.amount_relative_near = 1
                self.amount_near = 1
                if other_bug is not self:
                    dist = other_bug.pos.distance_to(self.pos)
                    if self.canibal:
                        #this checks to see if the bug is a canibal
                        if dist <= self.radius * 2:
                            self.amount_near += 1
                            if Bug.random_range(0, 1) < self.accuracy:
                                self._attack(screen, other_bug, True)
                    else:
                        #if bug is not canibal then it wont eat others with same color
                        if self.color != other_bug.color:
                            if dist <= self.radius * 2:
                                self.amount_relative_near += 1
                                if Bug.random_range(0, 1) < self.accuracy:
                                    self._attack(screen, other_bug)
                    if self.attached_bug_dist > dist:
                        self.attached_to = other_bug
                        self.attached_bug_dist = dist

            # Check mouse proximity for stat display
            dist_to_mouse = self.pos.distance_to(Bug.mouse_pos)
            if dist_to_mouse < Bug.scroll_wheel_range:
                self.draw_stat = True
            else:
                self.draw_stat = False

    def _attack(self, screen, other_bug, reflect=False):
        amount_remove = other_bug.defense - self.attack
        if amount_remove > 0:
            if other_bug.radius - amount_remove > 0:
                # Attack visual
                # pygame.draw.line(screen, (255,255,255,1), self.pos, other_bug.pos)

                # Remove radius from enemy
                other_bug.radius -= amount_remove

                # Balanced growth
                self._grow(amount_remove, other_bug)
            else:
                # Kill bug and eat rest
                remaining = other_bug.radius
                other_bug.radius = 0
                other_bug.dead = True

                self._grow(remaining, other_bug)
        if reflect:
            # If the target has higher attack or defense, it deals damage back.
            reflect_damage = other_bug.attack - self.defense
            if reflect_damage > 0:
                # Counter-hit visual (just weaker)
                # pygame.draw.line(screen, (255, 100, 100, 1), other_bug.pos, self.pos)
                if self.radius - reflect_damage > 0:
                    self.radius -= reflect_damage
                else:
                    # This ant dies from reflect damage
                    self.radius = 0
                    self.dead = True

    #helper functions
    def _create_bug(self, pos = None, brain = Brain.Brain()):
        if pos == None:
            pos = (int(Bug.random_range(0, Bug.screenWidth)), int(Bug.random_range(0, Bug.screenHeight)))
        Bug.bugs.append(Bug(pos, pos, self.color, self.speed, self.attack, self.defense, self.mutation_chance, self.accuracy, self.passive_eat, self.death_chance, self.reproduction_chance, self.canibal, brain))

    def create_bug_rand(bug_arr, brain = None):
        if brain == None:
            brain = Brain.Brain()
        pos = (int(Bug.random_range(0, Bug.screenWidth)), int(Bug.random_range(0, Bug.screenHeight)))
        bug_arr.append(Bug(pos, pos, (Bug.random_stat_range("color"),Bug.random_stat_range("color"),Bug.random_stat_range("color")), Bug.random_stat_range("speed"), Bug.random_stat_range("attack"), Bug.random_stat_range("defense"), Bug.random_stat_range("mutation"), Bug.random_stat_range("accuracy"), Bug.random_stat_range("passive eat"), Bug.random_stat_range("death"), Bug.random_stat_range("reproduction"), False, brain))
        # Bug.debug_stuff("Created a bug!!")

    def create_bug_and_return():
        pos = pygame.Vector2(Bug.random_range(0, Bug.screenWidth), Bug.random_range(0, Bug.screenHeight))
        # Bug.debug_stuff("Returned a bug!!")
        return(Bug(pos, pos , (Bug.random_stat_range("color"),Bug.random_stat_range("color"),Bug.random_stat_range("color")), Bug.random_stat_range("speed"), Bug.random_stat_range("attack"), Bug.random_stat_range("defense"), Bug.random_stat_range("mutation"), Bug.random_stat_range("accuracy"), Bug.random_stat_range("passive eat"), Bug.random_stat_range("death"), Bug.random_stat_range("reproduction")))
        
    def random_range(a, b):
        return a + (b - a) * (secrets.randbits(52) / (1 << 52))

    def random_stat_range(stat_name):
        low, high = Bug.max_ranges[stat_name]
        return Bug.random_range(low, high)

    def create_bug_amount(amount, bug_arr , UE , effect_universe = False , brain = None):
        try:
            # Bug.debug_stuff(f"Going to make {amount} of bugs")
            for i in range(amount):
                # Bug.debug_stuff(f"Created: {i} / {amount} bugs ")
                Bug.create_bug_rand(bug_arr, brain)
                if effect_universe:
                    UE[0] -= Bug.bug_energy_cost
        except:
            print("Not a valid array")

    def debug_stuff(text):
        print("Debug: " + text)
 
    #Draw helper functions
    def make_surface(self, size, color):
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        surf.fill(color)
        return surf
    
    def update_surface(self):
        self.image = self.make_surface(self.radius, self.color)

    def mouse_stat_pos(pos, s):
        Bug.mouse_pos = pos
        Bug.scroll_wheel_range = s

    def thinkFoward(self):
        self.brain.information[0] = self.amount_near
        self.brain.information[1] = self.direction[0]
        self.brain.information[2] = self.direction[1]
        self.brain.information[3] = self.speed
        self.brain.information[9] = self.attack
        self.brain.information[10] = self.defense
        self.brain.information[11] = self.accuracy
        self.brain.information[12] = self.times_split
        self.brain.information[13] = self.time_alive
        self.brain.information[14] = Bug.mouse_pos[0]
        self.brain.information[15] = Bug.mouse_pos[1]

        if self.attached_to:
            self.brain.information[4] = self.attached_to.pos[0]
            self.brain.information[5] = self.attached_to.pos[1]
            self.brain.information[6] = (self.attached_to.color[0] + self.attached_to.color[1] + self.attached_to.color[2]) / 3
            self.brain.information[7] = self.attached_to.attack
            self.brain.information[8] = self.attached_to.defense

        out, action = self.brain.brainThink()
        horizontal = (out[0] - 0.5) - (out[1] - 0.5)
        vertical   = (out[2] - 0.5) - (out[3] - 0.5)

        self.do_attack  = action[0] > 0.5
        self.do_breed   = action[1] > 0.5
        self.do_breed_other = action[2] > 0.5

        self.direction = pygame.Vector2(horizontal, vertical)