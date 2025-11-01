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
universe_energy = [1000]   # shared reference
universe_energy_decay = 0.1

font = pygame.font.SysFont("arial", 36)  # (font_name, size)

class bug:
    def __init__(self):
        self.bug_pos = pygame.Vector2(random.randrange(0 , screen.get_width()) , random.randrange(0, screen.get_height()))
        self.velocity = pygame.Vector2(0,0)
        self.acceleration = 400 #pixels per second^2
        self.direction = pygame.Vector2(random.uniform(-1, 1), random.uniform(-1, 1)).normalize()
        self.move = pygame.Vector2(0,0)
        self.radius = 10
        # each bug changes direction at a random interval (0.5–2.0s)
        self.change_interval = random.uniform(0.5, 2.0)
        # random starting offset to desynchronize timers
        self.change_timer = random.uniform(0, self.change_interval)

        self.attack = random.uniform(0, 1.0)
        self.defense = random.uniform(0, 1.0)
        # self.accuracy = random.uniform(0, 10)
        self.bug_attached = None

    def update(self, dt, universe_energy):
        self.radius -= universe_energy_decay
        universe_energy[0] += universe_energy_decay

        self.change_timer += dt
        if self.change_timer >= self.change_interval:
            self.direction = pygame.Vector2(random.uniform(-1, 1), random.uniform(-1, 1)).normalize()
            self.change_timer = 0
            self.change_interval = random.uniform(0.5, 2.0)  # pick a new interval each time

        # Apply movement
        self.velocity += self.direction * (self.acceleration / self.radius * 20) * dt
        self.velocity *= 0.85  # friction/damping
        self.bug_pos += self.velocity * dt

        # Keep bug within window bounds
        if self.bug_pos.x - self.radius < 0:
            self.bug_pos.x = self.radius
            self.velocity.x *= -0.5
        if self.bug_pos.x + self.radius > screen.get_width():
            self.bug_pos.x = screen.get_width() - self.radius
            self.velocity.x *= -0.5
        if self.bug_pos.y - self.radius < 0:
            self.bug_pos.y = self.radius
            self.velocity.y *= -0.5
        if self.bug_pos.y + self.radius > screen.get_height():
            self.bug_pos.y = screen.get_height() - self.radius
            self.velocity.y *= -0.5

    def draw(self, screen):
        pygame.draw.circle(screen, "red", self.bug_pos, self.radius)

    def detectNear(self, screen, bugs):
        for other_bug in bugs:
            if other_bug != self:
                if other_bug.radius < 5:
                    bugs.remove(other_bug)
                else:
                    other_bug_distance = other_bug.bug_pos.distance_to(self.bug_pos)
                    if other_bug_distance <= 1000:
                        pygame.draw.line(screen, "white", other_bug.bug_pos, self.bug_pos, 1)
                        self.bug_attached = other_bug
                        if other_bug.defense < self.attack:
                            attack = other_bug.defense - self.attack
                            other_bug.radius -= attack
                            self.radius += attack

bug_energy_cost = 10
bug_count = int(universe_energy[0] / bug_energy_cost)
universe_energy[0] -= bug_count * bug_energy_cost
bugs = [bug() for _ in range(bug_count)]  # this loop makes 25 bugs

# Main loop
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    # Fill the screen
    screen.fill("black")

    text_surface = font.render(f"Universe Energy {universe_energy[0]:.2f}", True, (255,255,255))

    for b in bugs:
        b.update(dt, universe_energy)
        b.draw(screen)
        b.detectNear(screen, bugs)

    screen.blit(text_surface, (100, 100))  # position on screen

    # Flip display
    pygame.display.flip()

    # Cap FPS and get delta time
    dt = clock.tick(60) / 1000

pygame.quit()
