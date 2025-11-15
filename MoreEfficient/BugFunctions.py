import pygame, secrets
import numpy as np

class Bug():
    bug_energy_cost = 10

    max_ranges = {
        "speed": [0 , 4.0],
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
    input_size = 4
    hidden_size = 10
    output_size = 4

    bugs = []

    def __init__(self, pos, posGrid, color, speed, attack, defense, mutation_chance, accuracy, passive_eat, death_chance, reproduction_chance, canibal):
        #Position and direction attributes
        self.pos = pygame.Vector2(pos)
        self.pos_grid = posGrid
        self.vel = pygame.Vector2(0, 0)
        self.direction = pygame.Vector2(0 , 0)
        self.image = self.make_surface(Bug.bug_energy_cost, color)
        self.draw_stat = False

        # weights and biases
        # weights and biases
        self.W1 = np.array([[Bug.random_range(-1, 1) for _ in range(Bug.input_size)]
            for _ in range(Bug.hidden_size)])

        self.b1 = np.array([Bug.random_range(-1, 1) for _ in range(Bug.hidden_size)])

        self.W2 = np.array([[Bug.random_range(-1, 1) for _ in range(Bug.hidden_size)]
            for _ in range(Bug.output_size)])

        self.b2 = np.array([Bug.random_range(-1, 1) for _ in range(Bug.output_size)])

        self.bug_information = np.array([0 , 0 , 0 , 0])

        #General Stats for bug
        self.color = color
        self.time_alive = 0
        self.change_timer = 0
        self.change_interval = 0
        self.times_split = 0
        self.dead = False

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

        #Text initalizations
        self.bug_age = None
        self.bug_stat_text = None
        self.bug_stat_text_1 = None
        
    def _update(self, dt, screen, UE, bugs):
        Bug.universe_energy = UE
        Bug.bugs=bugs
        Bug.screenWidth = screen.get_width()
        Bug.screenHeight = screen.get_height()

        if not self.dead:
            #Runs timer that moves bug at set intervals
            self.change_timer += dt
            if self.change_timer >= self.change_interval:
                Bug.brainThink(self, self.bug_information)
                self.change_timer = 0
                self.change_interval = Bug.random_range(Bug.change_interval_range[0], Bug.change_interval_range[1])

            #gives bugs movement
            effective_radius = max(self.radius, 10)
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
        Bug._detect_near(self,screen,dt)
        Bug._reproduce(self)
    
    def _draw(self, screen, font):
        pygame.draw.circle(screen, self.color, self.pos, self.radius)
        # pygame.draw.rect(screen, self.color, (self.pos.x, self.pos.y, self.radius, self.radius))
        if font:
            bug_amount = 0
            if self.attached_to != None:
                bug_amount = len(self.attached_to)
            if self.draw_stat:
                self.bug_age = font.render(f"Age: {self.time_alive}", True, (255, 255, 255))
                self.bug_stat_text = font.render(f"Atk: {self.attack:.2f} , Def: {self.defense:.2f}, Size: {self.radius:.2f}", True, (255,255,255))
                self.bug_stat_text_1 = font.render(f"PasEat: {self.passive_eat:.2f} , Split: {self.times_split}, MutCha: {self.mutation_chance:.2f}", True, (255,255,255))
                # self.bug_grid_pos_text = font.render(f"Grid Pos: {self.pos_grid} , Bugs near: {bug_amount}", True, (255,255,255))

                screen.blit(self.bug_age, (self.pos.x , self.pos.y + 10))
                # screen.blit(self.bug_grid_pos_text, (self.pos.x , self.pos.y - 20))
                if not self.dead:
                    screen.blit(self.bug_stat_text, (self.pos.x , self.pos.y))
                    screen.blit(self.bug_stat_text_1, (self.pos.x , self.pos.y - 10))

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

        Bug.update_surface()

    def _reproduce(self):
        if not self.dead and self.radius > Bug.bug_energy_cost * 2:
            if Bug.random_range(0 , 1.0) <= self.reproduction_chance:
                if self.radius >= Bug.bug_energy_cost:
                    #creates a new bug
                    Bug._create_bug(self, (self.pos.x + Bug.random_range(-self.radius * 2, self.radius * 2), self.pos.y + Bug.random_range(-self.radius * 2 , self.radius * 2)) )
                    self._grow(-Bug.bug_energy_cost)
                    self.times_split += 1

                    Bug.update_surface(self)

    def _grow(self, amount):
        self.radius += amount
        self.update_surface()

    def _age(self):
        self.time_alive += 1
        if Bug.random_range(0, 1) <= self.death_chance:
            self.defense = 0
            self.attack = 0
            self.dead = True
            self.color = "gray"
            Bug.update_surface()
    
    def _detect_near(self, screen, dt):
        if not self.dead:
            # Check interactions with other bugs
            for other_bug in Bug.bugs:
                if other_bug is not self:
                    if self.canibal:
                        #this checks to see if the bug is a canibal
                        dist = other_bug.pos.distance_to(self.pos)
                        if dist <= self.radius * 2:
                            if Bug.random_range(0, 1) < self.accuracy:
                                self._attack(screen, other_bug)
                    else:
                        #if bug is not canibal then it wont eat others with same color
                        if self.color != other_bug.color:
                            dist = other_bug.pos.distance_to(self.pos)
                            if dist <= self.radius * 2:
                                if Bug.random_range(0, 1) < self.accuracy:
                                    self._attack(screen, other_bug)
            # Check mouse proximity for stat display
            dist_to_mouse = self.pos.distance_to(Bug.mouse_pos)
            if dist_to_mouse < Bug.scroll_wheel_range:
                self.draw_stat = True
            else:
                self.draw_stat = False

    def _attack(self, screen, other_bug):
        amount_remove = other_bug.defense - self.attack
        if amount_remove > 0:
            if other_bug.radius - amount_remove > 0:
                # pygame.draw.line(screen, (255,255,255,1), self.pos, other_bug.pos)
                other_bug.radius -= amount_remove
                self._grow(amount_remove)
            else:
                other_bug.radius = 0
                other_bug.dead = True

    #helper functions
    def _create_bug(self, pos = None):
        if pos == None:
            pos = (int(Bug.random_range(0, Bug.screenWidth)), int(Bug.random_range(0, Bug.screenHeight)))
        Bug.bugs.append(Bug(pos, pos, self.color, self.speed, self.attack, self.defense, self.mutation_chance, self.accuracy, self.passive_eat, self.death_chance, self.reproduction_chance, self.canibal))

    def create_bug_rand(bug_arr):
        pos = (int(Bug.random_range(0, Bug.screenWidth)), int(Bug.random_range(0, Bug.screenHeight)))
        bug_arr.append(Bug(pos, pos, (Bug.random_stat_range("color"),Bug.random_stat_range("color"),Bug.random_stat_range("color")), Bug.random_stat_range("speed"), Bug.random_stat_range("attack"), Bug.random_stat_range("defense"), Bug.random_stat_range("mutation"), Bug.random_stat_range("accuracy"), Bug.random_stat_range("passive eat"), Bug.random_stat_range("death"), Bug.random_stat_range("reproduction"), False))
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

    def create_bug_amount(amount, bug_arr , UE , effect_universe = False):
        try:
            # Bug.debug_stuff(f"Going to make {amount} of bugs")
            for i in range(amount):
                # Bug.debug_stuff(f"Created: {i} / {amount} bugs ")
                Bug.create_bug_rand(bug_arr)
                if effect_universe:
                    UE -= Bug.bug_energy_cost
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

    def mouse_stat_pos(x, y, s):
        Bug.mouse_pos = pygame.Vector2(x , y)
        Bug.scroll_wheel_range = s

    def sigmoid(x):
        return 1 / (1 + np.exp(-x))
    
    def brainThink(self, x = np.array([0,0,0,0])):
        # Shared hidden layer
        z1 = np.dot(self.W1, x) + self.b1
        hidden = Bug.sigmoid(z1)

        # Output head 1
        z2 = np.dot(self.W2, hidden) + self.b2
        out = Bug.sigmoid(z2)
        if out[0] > out[1]:
            self.direction[0] = out[0]
        else:
            self.direction[0] = -out[1]

        if out[2] > out[3]:
            self.direction[1] = out[2]
        else:
            self.direction[1] = -out[3]