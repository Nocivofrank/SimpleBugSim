import pygame, random, threading
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
    screen = pygame.display.set_mode((300, 300), pygame.RESIZABLE)
    clock = pygame.time.Clock()
    running = True
    delta_Time = 0

    #setting universe Attributes
    universe_energy_max = 10000
    universe_energy = [universe_energy_max]

    #font initialization
    ui_Font = pygame.font.SysFont("arial", 30)
    bug_stat_font = pygame.font.SysFont("arial", 10)

    Bug.screenHeight = screen.get_height()
    Bug.screenWidth = screen.get_width()

    #this is where you will put all the code for the bug creation thing

    bugs = []

    Bug.debug_stuff(f"{len(bugs)} in original array")

    # Bug.create_bug_rand(bugs)
    Bug.debug_stuff(f"{len(bugs)} after adding one")
    Bug.create_bug_amount(1000 , bugs, universe_energy[0], True)
    # Bug.debug_stuff(f"{len(bugs)} after adding 100000 bugs using create_bug_amount()")

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        mouse_x, mouse_y = pygame.mouse.get_pos()
        Bug.mouse_stat_pos(mouse_x, mouse_y)
        print(mouse_x, mouse_y)

        screen.fill("black")
        if len(bugs) != 0:
            for b in bugs:
                b._update(delta_Time, screen, universe_energy[0], bugs)
                b._draw(screen, bug_stat_font)

        # Flip display
        pygame.display.flip()

        # Cap FPS and get delta time
        delta_Time = clock.tick(120) / 100

    pygame.quit()

threading.Thread(target=Simulation, daemon=True).start()
Graph.run()