import pygame
import random

seed = 5
random.seed(seed)

# Initialize pygame
pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True
dt = 0
universe_energy_max = 1000
universe_energy = [universe_energy_max]   # shared reference

new_bug_energy_cost = 10

font = pygame.font.SysFont("arial", 36)  # (font_name, size)
bug_font = pygame.font.SysFont("arial", 10)

class bug:
    def __init__(self, pos, speed, attack, defense, mutation_chance, passive_eat, spontaneous_death_chance, reproduction_chance):
        self.bug_pos = pos
        self.velocity = pygame.Vector2(0,0)
        self.acceleration = speed
        self.direction = pygame.Vector2(random.uniform(-1, 1), random.uniform(-1, 1)).normalize()
        self.move = pygame.Vector2(0,0)
        self.radius = new_bug_energy_cost
        self.initial_radius = self.radius
        # each bug changes direction at a random interval (0.5–2.0s)
        self.change_interval = random.uniform(0.5, 2.0)
        # random starting offset to desynchronize timers
        self.change_timer = random.uniform(0, self.change_interval)

        self.color = "red"
        self.time_alive = 0

        self.attack = attack
        self.defense = defense
        self.chance_for_mutation = mutation_chance
        self.reproduction_chance = reproduction_chance
        # self.accuracy = random.uniform(0, 10)
        self.bug_attached = None
        self.times_split = 0
        self.passive_eat = passive_eat
        self.spontaneous_death_chance = spontaneous_death_chance

        self.bug_age = bug_font.render(f"Age: {self.time_alive}", True, (255, 255, 255))
        self.bug_stat_text = bug_font.render(f"Atk: {self.attack:.2f} , Def: {self.defense:.2f}, Size: {self.radius}", True, (255,255,255))
        self.bug_stat_text_1 = bug_font.render(f"PasEat: {self.passive_eat:.2f} , Split: {self.times_split}, MutCha: {self.chance_for_mutation:.2f}", True, (255,255,255))
        self.mutate()

    def update(self, dt, universe_energy, bugs):
        self.change_timer += dt
        if self.change_timer >= self.change_interval:
            self.direction = pygame.Vector2(random.uniform(-1, 1), random.uniform(-1, 1)).normalize()
            self.change_timer = 0
            self.change_interval = random.uniform(0.5, 2.0)  # pick a new interval each time

        # Apply movement
        effective_radius = max(self.radius, 10)
        self.velocity += self.direction * (self.acceleration / effective_radius * 20) * dt
        self.velocity *= 0.85  # friction/damping
        self.bug_pos += self.velocity * dt

        # Keep bug within window bounds (wrap around edges)
        if self.bug_pos.x < -self.radius:
            self.bug_pos.x = screen.get_width() + self.radius
        elif self.bug_pos.x > screen.get_width() + self.radius:
            self.bug_pos.x = -self.radius

        if self.bug_pos.y < -self.radius:
            self.bug_pos.y = screen.get_height() + self.radius
        elif self.bug_pos.y > screen.get_height() + self.radius:
            self.bug_pos.y = -self.radius
        
        self.reproduce()
        self.bug_age = bug_font.render(f"Age: {self.time_alive}", True, (255, 255, 255))
        self.bug_stat_text = bug_font.render(f"Atk: {self.attack:.2f} , Def: {self.defense:.2f}, Size: {self.radius:.2f}", True, (255,255,255))
        self.bug_stat_text_1 = bug_font.render(f"PasEat: {self.passive_eat:.2f} , Split: {self.times_split}, MutCha: {self.chance_for_mutation:.2f}", True, (255,255,255))

    def mutate(self):
        # small helper function
        def maybe_mutate(value, min_val, max_val, intensity=0.2):
            """Mutate value slightly with given chance and intensity."""
            if random.random() <= self.chance_for_mutation:
                # bias toward small changes instead of total random resets
                delta = random.uniform(-intensity, intensity)
                new_value = value + delta
                return max(min_val, min(max_val, new_value))
            return value

        # Apply mutations to each trait
        self.attack = maybe_mutate(self.attack, 0, 1)
        self.defense = maybe_mutate(self.defense, 0, 1)
        self.chance_for_mutation = maybe_mutate(self.chance_for_mutation, 0, 1)
        self.change_interval = maybe_mutate(self.change_interval, 0.3, 3.0)
        self.spontaneous_death_chance = maybe_mutate(self.spontaneous_death_chance, 0, 1)
        self.reproduction_chance = maybe_mutate(self.reproduction_chance, 0, 1)

    def reproduce(self):
        # this is where the bugs reproduce
        if random.random() <= self.reproduction_chance and universe_energy[0] > universe_energy_max/10:
            if self.radius >= new_bug_energy_cost:
                bugs.append(bug(pygame.Vector2(random.randrange(0 , screen.get_width()) , random.randrange(0, screen.get_height())), self.acceleration, self.attack, self.defense, self.chance_for_mutation, self.passive_eat, self.spontaneous_death_chance, self.reproduction_chance))
                self.radius -= new_bug_energy_cost
                self.times_split += 1

    def draw(self, screen):
        pygame.draw.circle(screen, 255, self.bug_pos, self.radius)
        screen.blit(self.bug_age, (self.bug_pos.x - self.radius * 2, self.bug_pos.y + 10))
        screen.blit(self.bug_stat_text, (self.bug_pos.x - self.radius * 2, self.bug_pos.y))  # position on screen
        screen.blit(self.bug_stat_text_1, (self.bug_pos.x - self.radius * 2, self.bug_pos.y - 10))  # position on screen

    def detectNear(self, screen, bugs):
        amount_near = 0
        for other_bug in bugs:
            if other_bug != self:
                dist = other_bug.bug_pos.distance_to(self.bug_pos)
                if dist <= self.radius * 2:
                    amount_near += 1
                    self.do_attack(screen, other_bug)
            if universe_energy[0] > self.passive_eat:
                self.radius += self.passive_eat * dt
                universe_energy[0] -= self.passive_eat * dt

    def do_attack(self, screen, other_bug):
        pygame.draw.line(screen, "white", other_bug.bug_pos, self.bug_pos, 1)
        attack_value = self.attack - other_bug.defense
        if attack_value > 0 and self.radius > new_bug_energy_cost / 2:
            self.radius += attack_value # smaller reward to avoid runaway growth
            other_bug.radius -= attack_value

    def age(self):
        self.time_alive += 1
        if random.random() <= self.spontaneous_death_chance:
            self.defense = 0
            self.defense = 0
# bug_count = int(universe_energy[0] / new_bug_energy_cost)
# universe_energy[0] -= bug_count * new_bug_energy_cost
# bugs = [bug(pygame.Vector2(random.randrange(0 , screen.get_width()) , random.randrange(0, screen.get_height())),speed=random.randrange(0,1000), attack=random.uniform(0,1.0), defense=random.uniform(0,1.0), mutation_chance=random.uniform(0,1.0), passive_eat=random.uniform(0,1.0)) for _ in range(bug_count)]  # this loop makes 25 bugs
bugs = []
while universe_energy[0] > new_bug_energy_cost:
    universe_energy[0] -= new_bug_energy_cost
    bugs.append(bug(pygame.Vector2(random.randrange(0 , screen.get_width()) , random.randrange(0, screen.get_height())),speed=random.randrange(0,1000), attack=random.uniform(0,1.0), defense=random.uniform(0,1.0), mutation_chance=random.uniform(0,1.0), passive_eat=random.uniform(0,1.0), spontaneous_death_chance=random.uniform(0,1.0), reproduction_chance=random.uniform(0,1.0)))
world_speed = 100000

update_bugs = True
bug_timer = 0

# Main loop
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                world_speed *= 10
            elif event.key == pygame.K_DOWN:
                world_speed /= 10
            elif event.key == pygame.K_SPACE:
                world_speed = 1000
            elif event.key == pygame.K_0:
                update_bugs = False
            elif event.key == pygame.K_1:
                update_bugs = True

    # Fill the screen
    screen.fill("black")

    new_bugs = []

    for b in bugs:
        if update_bugs:
            b.update(dt, universe_energy, new_bugs)
        b.draw(screen)
        b.detectNear(screen, bugs)
        if b.radius < 1:
            if b.radius < 0:
                b.radius = 0
            universe_energy[0] += b.radius
            b.radius = 0
            bugs.remove(b)
    
    bugs.extend(new_bugs)

    text_surface = font.render(f"Energy: {universe_energy[0]:.2f}", True, (255,255,255))
    bug_amount = font.render(f"Bugs: {len(bugs)}", True, (255,255,255))
    debug = font.render(f"Paused: {update_bugs}", True, (255,255,255))
    screen.blit(debug, (100, 0))
    screen.blit(text_surface, (100, 100))
    screen.blit(bug_amount, (100, 200))

    # Flip display
    pygame.display.flip()

    # Cap FPS and get delta time
    dt = clock.tick(120) / world_speed
    bug_timer += dt
    if bug_timer > 1:
        for b in bugs:
            bug_timer = 0
            b.age()

pygame.quit()
