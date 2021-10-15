import math

import networkx as nx
from mesa import Model
from mesa.datacollection import DataCollector
from mesa.space import NetworkGrid
from mesa.time import RandomActivation
from .VirusAgent import State, VirusAgent


def number_state(model, state):
    return sum([1 for a in model.grid.get_all_cell_contents() if a.state is state])


def number_infected(model):
    # return the number of INFECTED agents belonging to model
    # NB: use the helper method "number_state"
    return number_state(model, State.INFECTED)

def number_susceptible(model):
    # return the number of SUSCEPTIBLE agents belonging to model
    # NB: use the helper method "number_state"
    return number_state(model, State.SUSCEPTIBLE)


def number_resistant(model):
    # return the number of RESISTANT agents belonging to model
    # NB: use the helper method "number_state"
    return number_state(model, State.RESISTANT)


class VirusOnNetwork(Model):
    """A virus model with some number of agents"""
    def __init__(self, num_nodes=10, avg_node_degree=3, initial_outbreak_size=1, virus_spread_chance=0.4,
                 virus_check_frequency=0.4, recovery_chance=0.3, gain_resistance_chance=0.5):
        super().__init__()
        self.num_nodes = num_nodes
        prob = avg_node_degree / self.num_nodes
        self.G = nx.erdos_renyi_graph(n=self.num_nodes, p=prob)
        self.grid = NetworkGrid(self.G)
        self.schedule = RandomActivation(self)
        self.initial_outbreak_size = initial_outbreak_size if initial_outbreak_size <= num_nodes else num_nodes
        self.virus_spread_chance = virus_spread_chance
        self.virus_check_frequency = virus_check_frequency
        self.recovery_chance = recovery_chance
        self.gain_resistance_chance = gain_resistance_chance
        self.datacollector = DataCollector({"Infected": number_infected,
                                            "Susceptible": number_susceptible,
                                            "Resistant": number_resistant})

        # Create agents placing them on a NetworkGrid
        for i, node in enumerate(self.G.nodes()):
            a = VirusAgent(i, self, State.SUSCEPTIBLE, self.virus_spread_chance, self.virus_check_frequency,
                           self.recovery_chance, self.gain_resistance_chance)
            self.schedule.add(a)
            # Add the agent to the node
            self.grid.place_agent(a, node)

        # Infect some nodes according to initial_outbreak_size
        infected_nodes = self.random.sample(self.G.nodes(), self.initial_outbreak_size)
        for a in self.grid.get_cell_list_contents(infected_nodes):
            a.state = State.INFECTED

        self.running = True
        self.datacollector.collect(self)

    def resistant_susceptible_ratio(self):
        try:
            return number_state(self, State.RESISTANT) / number_state(self, State.SUSCEPTIBLE)
        except ZeroDivisionError:
            return math.inf

    def step(self):
        self.schedule.step()
        # collect data
        self.datacollector.collect(self)

    def run_model(self, n):
        for i in range(n):
            self.step()
