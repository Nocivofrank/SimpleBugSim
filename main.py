import pygame, random, threading, secrets
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtWidgets

#shared data

data_time = []
data_energy = []
data_bugcount = []
data_radius_avg = []
data_immortal = []

lock = threading.Lock()

#########################
#PyqtGraph window initialization
app = QtWidgets.QApplication([])
win = pg.GraphicsLayoutWidget(title="Bug Simulation Stats")
plot = win.addPlot(title="Universe Energy / Bug Count / Size")
plot.showGrid(x=True, y=True)
plot.addLegend()
plot.setLabel('left', 'Value', units='Energy / Population / Radius')
plot.setLabel('bottom', 'Time', units='s')

#making the values go up the y axis when increasing
plot.invertY(False)

#giving curves attributes
energy_curve = plot.plot(pen=pg.mkPen('y', width=2), name="Energy")
bugs_curve   = plot.plot(pen=pg.mkPen('g', width=2), name="Bug Count")
radius_curve = plot.plot(pen=pg.mkPen('b', width=2), name="Average Radius")
immortal_curve = plot.plot(pen=pg.mkPen('r', width=2), name="Immortal")


win.show()

def update_plot():
    with lock:
        if len(data_time) > 0:
            # Scale data to comparable ranges
            max_energy = max(data_energy) if max(data_energy) != 0 else 1
            max_bugs = max(data_bugcount) if max(data_bugcount) != 0 else 1
            max_radius = max(data_radius_avg) if max(data_radius_avg) != 0 else 1
            max_immortal = max(data_immortal) if max(data_immortal) != 0 else 1

            energy_curve.setData(data_time, [e / max_energy for e in data_energy])
            bugs_curve.setData(data_time, [b / max_bugs for b in data_bugcount])
            radius_curve.setData(data_time, [r / max_radius for r in data_radius_avg])
            immortal_curve.setData(data_time, [i / max_immortal for i in data_immortal])

            if data_time[-1] > 20:
                plot.setXRange(data_time[-1] - 20, data_time[-1])
            else:
                plot.setXRange(0, 20)
            plot.enableAutoRange('y', True)


timer = QtCore.QTimer()
timer.timeout.connect(update_plot)
timer.start(100)  # update every 100 ms

###


##Mat plot lib stuff on top


###
# made this into function to multi-thread
def run_sim():
    seed = 5
    random.seed(seed)

    # Initialize pygame
    pygame.init()
    screen = pygame.display.set_mode((500,500))
    clock = pygame.time.Clock()
    running = True
    dt = 0

    #giving universe set max amount of energy
    universe_energy_max = 100000
    universe_energy = [universe_energy_max]

    #cost for creating a new bug
    new_bug_energy_cost = 10

    #font initialization for text
    font = pygame.font.SysFont("arial", 36)
    bug_font = pygame.font.SysFont("arial", 10)

    def random_range(a, b):
        return a + (b - a) * (secrets.randbits(52) / (1 << 52))

    class bug:
        def __init__(self, pos, speed, attack, defense, mutation_chance, passive_eat, spontaneous_death_chance, reproduction_chance):
            self.bug_pos = pos
            self.velocity = pygame.Vector2(0,0)
            self.direction = pygame.Vector2(random_range(-1, 1), random_range(-1, 1)).normalize()
            self.move = pygame.Vector2(0,0)
            self.change_interval = random_range(.5, 2.0)
            self.change_timer = random_range(0 , self.change_interval)

            self.color = "red"
            self.time_alive = 0
            self.times_split = 0

            ##### ----- Bug Attributes
            self.dead = False

            self.acceleration = speed
            self.radius = new_bug_energy_cost
            self.initial_radius = self.radius
            self.attack = attack
            self.defense = defense
            self.chance_for_mutation = mutation_chance
            self.reproduction_chance = reproduction_chance
            self.max_radius = self.initial_radius * 5
            # self.accuracy = random.uniform(0, 10)
            self.passive_eat = passive_eat
            self.spontaneous_death_chance = spontaneous_death_chance

            self.bug_attached = None

            #Text initalizations
            self.bug_age = bug_font.render(f"Age: {self.time_alive}", True, (255, 255, 255))
            self.bug_stat_text = bug_font.render(f"Atk: {self.attack:.2f} , Def: {self.defense:.2f}, Size: {self.radius}", True, (255,255,255))
            self.bug_stat_text_1 = bug_font.render(f"PasEat: {self.passive_eat:.2f} , Split: {self.times_split}, MutCha: {self.chance_for_mutation:.2f}", True, (255,255,255))
            #gives the bug a chance to mutate
            self.mutate()

        def update(self, dt, universe_energy, bugs):
            #applies universal decay to bug
            decay = 0
            decay += self.initial_radius * (.001 * self.radius) * dt
            if self.radius - decay < 0:
                self.radius = 0
            else:
                self.radius -= decay
                universe_energy[0] += decay

            #Runs timer that moves bug at set intervals
            self.change_timer += dt
            if self.change_timer >= self.change_interval:
                self.direction = pygame.Vector2(random_range(-1, 1), random_range(-1, 1)).normalize()
                self.change_timer = 0
                self.change_interval = random_range(.5, 2.0)

            if not self.dead:
                #gives bugs movement
                effective_radius = max(self.radius, 10)
                self.velocity += self.direction * (self.acceleration / effective_radius * 20) * dt
                self.velocity *= 0.85
                self.bug_pos += self.velocity * dt

            #wrap around edges
            if self.bug_pos.x < -self.radius:
                self.bug_pos.x = screen.get_width() + self.radius
            elif self.bug_pos.x > screen.get_width() + self.radius:
                self.bug_pos.x = -self.radius

            if self.bug_pos.y < -self.radius:
                self.bug_pos.y = screen.get_height() + self.radius
            elif self.bug_pos.y > screen.get_height() + self.radius:
                self.bug_pos.y = -self.radius
            
            #calls the self reproduce function that way it may reproduce more complicated in function
            if len(bugs) < 500:
                self.reproduce()
            # a bunch of gibrish but for text updating
            self.bug_age = bug_font.render(f"Age: {self.time_alive}", True, (255, 255, 255))
            self.bug_stat_text = bug_font.render(f"Atk: {self.attack:.2f} , Def: {self.defense:.2f}, Size: {self.radius:.2f}", True, (255,255,255))
            self.bug_stat_text_1 = bug_font.render(f"PasEat: {self.passive_eat:.2f} , Split: {self.times_split}, MutCha: {self.chance_for_mutation:.2f}", True, (255,255,255))

        def mutate(self):
            # small helper function
            def maybe_mutate(value, min_val, max_val, intensity=0.2):
                # basically (if mutation chance is 10% then it has a 10% of hitting)
                if random_range(0, 1) <= self.chance_for_mutation:
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
            self.passive_eat = maybe_mutate(self.passive_eat, 0, .5)
            self.spontaneous_death_chance = maybe_mutate(self.spontaneous_death_chance, 0, 1)
            self.reproduction_chance = maybe_mutate(self.reproduction_chance, 0, .2)

        def reproduce(self):
            # this is where the bugs reproduce checks chances of reproduction and if universe has enough energy available
            if random_range(0, 1) <= self.reproduction_chance and universe_energy[0] > universe_energy_max/10:
                #checks to see if the bug is big enough to give its energy to reproduce
                if self.radius >= new_bug_energy_cost:
                    #creating new bug
                    print("Bug Repro")
                    bugs.append(bug(pygame.Vector2(int(random_range(0, screen.get_width())) , int(random_range(0, screen.get_height()))), self.acceleration, self.attack, self.defense, self.chance_for_mutation, self.passive_eat, self.spontaneous_death_chance, self.reproduction_chance))
                    self.radius -= new_bug_energy_cost
                    self.times_split += 1

        def draw(self, screen):
            # umm cmon 
            pygame.draw.circle(screen, self.color, self.bug_pos, self.radius)
            screen.blit(self.bug_age, (self.bug_pos.x , self.bug_pos.y + 10))
            if not self.dead:
                screen.blit(self.bug_stat_text, (self.bug_pos.x , self.bug_pos.y))
                screen.blit(self.bug_stat_text_1, (self.bug_pos.x , self.bug_pos.y - 10))

        #funciton used to find bugs around bug
        def detectNear(self, screen, bugs):
            if not self.dead:
                amount_near = 0
                for other_bug in bugs:
                    if other_bug != self:
                        dist = other_bug.bug_pos.distance_to(self.bug_pos)
                        #if other bug is nearby it attacks that bug
                        if dist <= self.radius * 2:
                            amount_near += 1
                            self.do_attack(screen, other_bug)
                            #checks to see if it can eat from just existing
                        if self.radius <= self.max_radius:
                            if universe_energy[0] > self.passive_eat:
                                self.radius += self.passive_eat * dt
                                universe_energy[0] -= self.passive_eat * dt

        #CRAZY  ATTACKING  FUNCTION 
        def do_attack(self, screen, other_bug):
            pygame.draw.line(screen, "white", other_bug.bug_pos, self.bug_pos, 1)
            #checks to see if attack will surpase the defense amount
            attack_value = self.attack - other_bug.defense
            #checks to see if bug ate enough already
            if self.radius <= self.max_radius:
                if attack_value > 0 and self.radius > new_bug_energy_cost / 2:
                    self.radius += attack_value # smaller reward to avoid runaway growth
                    other_bug.radius -= attack_value

        #ages bug to keep death ineviatable
        def age(self):
            self.time_alive += 1
            if random_range(0, 1) <= self.spontaneous_death_chance:
                self.defense = 0
                self.attack = 0
                self.dead = True
                self.color = "gray"

    # creates bugs with all possible energy in the universe
    bugs = []
    # while universe_energy[0] > new_bug_energy_cost:
    #     universe_energy[0] -= new_bug_energy_cost
    #     bugs.append(bug(pygame.Vector2(random.randrange(0 , screen.get_width()) , random.randrange(0, screen.get_height())),speed=random.randrange(0,1000), attack=random.uniform(0,1.0), defense=random.uniform(0,1.0), mutation_chance=random.uniform(0,1.0), passive_eat=random.uniform(0,.5), spontaneous_death_chance=random.uniform(0.01,1.0), reproduction_chance=random.uniform(0,1.0)))

    MAX_POINTS = 10000

    def append_data():
        with lock:
            data_time.append(sim_time)
            data_energy.append(universe_energy[0])
            data_bugcount.append(live_bugs)
            data_radius_avg.append(total_bug_rad / max(1, len(bugs)))
            data_immortal.append(total_bug_immortal)

            # Rolling window
            if len(data_time) > MAX_POINTS:
                del data_time[:-MAX_POINTS]
                del data_energy[:-MAX_POINTS]
                del data_bugcount[:-MAX_POINTS]
                del data_radius_avg[:-MAX_POINTS]
                del data_immortal[:-MAX_POINTS]

    world_speed = 1000
    update_bugs = True
    bug_timer = 0
    sim_time = 0.0

    # Main loop
    while running:
        #gives the chance for spontaneos life
        if universe_energy[0] > new_bug_energy_cost and len(bugs) < 500:
            if random_range(0, 1) <= 0.01:
                universe_energy[0] -= new_bug_energy_cost
                print("Random Bug created", sim_time)
                bugs.append(bug(pygame.Vector2(int(random_range(0, screen.get_width())) , int(random_range(0, screen.get_height()))),speed=random.randrange(0,1000), attack=random.uniform(0,1.0), defense=random.uniform(0,1.0), mutation_chance=random.uniform(0,1.0), passive_eat=random.uniform(0,.2), spontaneous_death_chance=random.uniform(0.01,1.0), reproduction_chance=random.uniform(0,1.0)))

        if universe_energy[0] > universe_energy_max:
            universe_energy[0] = universe_energy_max
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
        live_bugs = 0

        total_bug_rad = 0
        total_bug_immortal = 0

        if len(bugs) != 0:
            for b in bugs:
                if not b.dead:
                    live_bugs += 1
                if update_bugs:
                    b.update(dt, universe_energy, bugs)
                    b.detectNear(screen, bugs)
                b.draw(screen)
                if b.radius < 1 or b.dead:
                    if b.radius < 0:
                        b.radius = 0
                    universe_energy[0] += b.radius
                    b.radius = 0
                    bugs.remove(b)
                total_bug_rad += b.radius
                if b.spontaneous_death_chance == 0:
                    total_bug_immortal += 1
            
            bugs.extend(new_bugs)

            text_surface = font.render(f"Resources: {universe_energy[0]:.2f}", True, (255,255,255))
            bug_amount = font.render(f"Bugs: {live_bugs}", True, (255,255,255))
            debug = font.render(f"Paused: {not update_bugs}", True, (255,255,255))
            screen.blit(debug, (100, 0))
            screen.blit(text_surface, (100, 100))
            screen.blit(bug_amount, (100, 200))

            # Flip display
            pygame.display.flip()

            # Cap FPS and get delta time
            dt = clock.tick(60) / world_speed

            sim_time += dt

            append_data()

            if update_bugs:
                bug_timer += dt
                if bug_timer > 1:
                    for b in bugs:
                        bug_timer = 0
                        b.age()

    pygame.quit()

threading.Thread(target=run_sim, daemon=True).start()

app.exec()