import pygame, random, threading
from GraphFunctions import Graph

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
    seed = 5
    random.seed(seed)

    #initializing pygame
    pygame.init()
    screen = pygame.display.set_mode()
    clock = pygame.time.Clock()
    running = True
    delta_Time = 0

    #setting universe Attributes
    universe_energy_max = 10000
    universe_energy = [universe_energy_max]

    #font initialization
    ui_Font = pygame.font.SysFont("arial", 30)
    bug_stat_font = pygame.font.SysFont("arial", 10)

    ###Dont FORGET to update the data for graph

threading.Thread(target=Simulation, daemon=True).start()
Graph.run()