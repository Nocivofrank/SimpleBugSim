import pygame, secrets

class Bug():
    bug_energy_cost = 10

    max_ranges = {
        "speed": [0 , 4.0],
        "attack": [0 , 1.0],
        "defense": [0 , 1.0],
        "mutation": [0 , 1.0],
        "passive eat": [0 , .5],
        "death": [0 , 1.0],
        "reproduction": [0 , 1.0],
        "size": [0 , 100],
        "color": [0 , 255]
    }

    change_interval_range = [ 0 , 10 ]

    universe_energy = None

    screenWidth = 0
    screenHeight = 0

    bugs = []

    def __init__(self, pos, color, speed, attack, defense, mutation_chance, passive_eat, death_chance, reproduction_chance):
        #Position and direction attributes
        self.pos = pygame.Vector2(pos)
        self.vel = pygame.Vector2(0, 0)
        self.direction = pygame.Vector2(Bug.random_range(-1,1), Bug.random_range(-1,1)).normalize()
        self.image = self.make_surface(Bug.bug_energy_cost, color)

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
        self.passive_eat = passive_eat
        self.death_chance = death_chance
        self.reproduction_chance = reproduction_chance

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
                self.direction = pygame.Vector2(Bug.random_range(-1, 1), Bug.random_range(-1, 1)).normalize()
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
    
    def _draw(self, screen, font, draw_text = False):
        pygame.draw.circle(screen, self.color, self.pos, self.radius)
        # pygame.draw.rect(screen, self.color, (self.pos.x, self.pos.y, self.radius, self.radius))
        if font and draw_text:
            self.bug_age = font.render(f"Age: {self.time_alive}", True, (255, 255, 255))
            self.bug_stat_text = font.render(f"Atk: {self.attack:.2f} , Def: {self.defense:.2f}, Size: {self.radius:.2f}", True, (255,255,255))
            self.bug_stat_text_1 = font.render(f"PasEat: {self.passive_eat:.2f} , Split: {self.times_split}, MutCha: {self.mutation_chance:.2f}", True, (255,255,255))

            screen.blit(self.bug_age, (self.pos.x , self.pos.y + 10))
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
        if not self.dead:
            if Bug.random_range(0 , 1.0) <= self.reproduction_chance:
                if self.radius >= Bug.bug_energy_cost:
                    #creates a new bug
                    Bug.create_bug()
                    self.radius -= Bug.bug_energy_cost
                    self.times_split += 1

                    Bug.update_surface()

    def _age(self):
        self.time_alive += 1
        if Bug.random_range(0, 1) <= self.death_chance:
            self.defense = 0
            self.attack = 0
            self.dead = True
            self.color = "gray"
            Bug.update_surface()
    
    #helper functions
    def _create_bug(self):
        pos = pygame.Vector2(Bug.random_range(0, Bug.screenWidth), Bug.random_range(0, Bug.screenHeight))
        Bug.bugs.append(Bug(pos, self.color, self.speed, self.attack, self.defense, self.mutation_chance, self.passive_eat, self.death_chance, self.reproduction_chance))

    def create_bug_rand(bug_arr):
        pos = pygame.Vector2(Bug.random_range(0, Bug.screenWidth), Bug.random_range(0, Bug.screenHeight))
        bug_arr.append(Bug(pos, (Bug.random_stat_range("color"),Bug.random_stat_range("color"),Bug.random_stat_range("color")), Bug.random_stat_range("speed"), Bug.random_stat_range("attack"), Bug.random_stat_range("defense"), Bug.random_stat_range("mutation"), Bug.random_stat_range("passive eat"), Bug.random_stat_range("death"), Bug.random_stat_range("reproduction")))
        # Bug.debug_stuff("Created a bug!!")

    def create_bug_and_return():
        pos = pygame.Vector2(Bug.random_range(0, Bug.screenWidth), Bug.random_range(0, Bug.screenHeight))
        # Bug.debug_stuff("Returned a bug!!")
        return(Bug(pos, (Bug.random_stat_range("color"),Bug.random_stat_range("color"),Bug.random_stat_range("color")), Bug.random_stat_range("speed"), Bug.random_stat_range("attack"), Bug.random_stat_range("defense"), Bug.random_stat_range("mutation"), Bug.random_stat_range("passive eat"), Bug.random_stat_range("death"), Bug.random_stat_range("reproduction")))
        
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

    def grow(self, amount):
        self.radius += amount
        self.update_surface()