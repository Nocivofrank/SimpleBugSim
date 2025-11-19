import pygame, threading
from GraphFunctions import Graph
from BugFunctions import Bug

# Shared Data for Graph
shared_data = {
    "time": [],
    "energy": [],
    "bugCount": [],
    "radius_avg": [],
    "immortals": []
}

#Creates the threading lock that way i can call function on diff thread
lock = threading.Lock()

#Creating a graph class from the GraphFunctions.py file
Graph = Graph()
Graph.set_data_sources(lock, shared_data)

def Simulation():
    #initializing pygame
    pygame.init()
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    clock = pygame.time.Clock()
    running = True
    delta_Time = 1000
    world_speed = 1000
    bug_age_Counter = 0

    #setting universe Attributes
    universe_energy_max = 10000
    universe_energy = [universe_energy_max]

    #font initialization
    ui_Font = pygame.font.SysFont("arial", 30)
    bug_stat_font = pygame.font.SysFont("arial", 10)
    scroll_wheel_value = 100

    Bug.screenHeight = screen.get_height()
    Bug.screenWidth = screen.get_width()

    #this is where you will put all the code for the bug creation thing

    bugs = []

    # Bug.debug_stuff(f"{len(bugs)} in original array")

    # # Bug.create_bug_rand(bugs)
    # Bug.debug_stuff(f"{len(bugs)} after adding one")
    amount_of_bugs = 500
    bugs_dead = False
    Bug.create_bug_amount(amount_of_bugs , bugs, universe_energy, True)
    # Bug.debug_stuff(f"{len(bugs)} after adding 100000 bugs using create_bug_amount()")

    closest_bug = None
    closest_bug_dist = 1000
    generation = 0

    mouse_pos = pygame.Vector2(Bug.random_range(0 , screen.get_width()) ,Bug.random_range(0 , screen.get_height()))
    mouse_direction = pygame.Vector2(Bug.random_range(-1 , 1), Bug.random_range(-1 , 1))

    mouseR = 25
    mouseColor = ( 0 , 255 , 255)
    

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEWHEEL:
                if event.y > 0:
                    scroll_wheel_value += 10
                elif event.y < 0:
                    scroll_wheel_value -= 10
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    world_speed *= 10
                elif event.key == pygame.K_DOWN:
                    world_speed /= 10
                elif event.key == pygame.K_SPACE:
                    world_speed = 1000

        bug_age = ui_Font.render(f"Generation : {generation}", True, (255, 255, 255))

        mouse_pos[1] += mouse_direction[1]
        mouse_pos[0] += mouse_direction[0]
        if mouse_pos[1] > screen.get_height():
            mouse_pos[1] = 0
        if mouse_pos[0] > screen.get_width():
            mouse_pos[0] = 0
            
        
        # mouse_pos = pygame.mouse.get_pos()
        Bug.mouse_stat_pos(mouse_pos, scroll_wheel_value)
        screen.fill("black")        
        
        pygame.draw.circle(screen, mouseColor, mouse_pos, mouseR)

        amount = int(300 / world_speed)
        if amount <= 0:
            amount = 1
        for i in range(amount):
            if len(bugs) != 0:
                bug_age_Counter += 1
                for b in bugs:
                    if b.pos.distance_to(mouse_pos) < closest_bug_dist:
                        closest_bug = b
                        closest_bug_dist = b.pos.distance_to(mouse_pos)
                    if not b.dead:
                        b._update(delta_Time, screen, universe_energy, bugs)
                        b._draw(screen, bug_stat_font)                
                        if bug_age_Counter > 60:
                            bug_age_Counter = 0
                            b._age()
                    if b.dead:
                        bugs.remove(b)
            if bugs_dead:
                Bug.create_bug_amount(amount_of_bugs, bugs, universe_energy, True, closest_bug.brain)
                bugs_dead = False
            # if len(bugs) < amount_of_bugs:
            #     Bug.create_bug_amount(1, bugs, universe_energy, True)

        if len(bugs) <= 0:
            generation += 1
            mouse_direction = pygame.Vector2(Bug.random_range(-1 , 1), Bug.random_range(-1 , 1))
            mouse_pos = pygame.Vector2(Bug.random_range(0 , screen.get_width()) ,Bug.random_range(0 , screen.get_height()))
            bugs_dead = True
                
        # for b in bugs:
        #     if not b.dead:

        print(f"fps: { world_speed * delta_Time}")
        # print(f"Amount of Bugs : {len(bugs)} , Universe Energy : {universe_energy[0]}")

        if len(bugs) <= 0:
            bugs_dead = True

        # Flip display
        pygame.display.flip()

        # Cap FPS and get delta time
        delta_Time = clock.tick(120) / world_speed

    pygame.quit()

threading.Thread(target=Simulation, daemon=True).start()
Graph.run()