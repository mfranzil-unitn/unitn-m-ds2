import random
from enum import Enum
from typing import List

from mesa import Agent


class State(Enum):
    SUSCEPTIBLE = 0
    INFECTED = 1
    RESISTANT = 2


class VirusAgent(Agent):
    def __init__(self, unique_id, model, initial_state, virus_spread_chance, virus_check_frequency,
                 recovery_chance, gain_resistance_chance):
        super().__init__(unique_id, model)
        # set initial state and all agent common paramters
        # e.g.: virus_spread_change, virus_check_frequency...
        self.state = initial_state
        self.virus_spread_chance = virus_spread_chance
        self.virus_check_frequency = virus_check_frequency
        self.recovery_chance = recovery_chance
        self.gain_resistance_chance = gain_resistance_chance

    def try_to_infect_neighbors(self):
        # Get your neighbors
        # NB: get_neigbors(pos, include_center=False) returns the (integer) ids of nodes around pos
        # while get_cell_list_contents([list of nodes]) gives you the agent instance representing those nodes
        neighbors_nodes = self.model.grid.get_cell_list_contents(
            self.model.grid.get_neighbors(self.pos, include_center=False)
        )
        # Keep a list of just scuscpetible neighbors, those that can be infected
        susceptible_nodes = [node for node in neighbors_nodes if node.state == State.SUSCEPTIBLE]

        # For each susceptible neighbors (let's call it q)
        for node in susceptible_nodes:
            # flip a virus_spread_chance coin
            # Head? Then q got infected!
            if random.uniform(0, 1) <= node.virus_spread_chance:
                node.state = State.INFECTED

    def try_gain_resistance(self):
        # Just flip a coin weighted according to "gain_resistance_chance"
        # if you're lucky you become "RESISTANT"
        if random.uniform(0, 1) <= self.gain_resistance_chance:
            self.state = State.RESISTANT

    def try_remove_infection(self):
        # Try to remove the infection according to recovery_chance
        if random.uniform(0, 1) <= self.recovery_chance:
            # if you have Success you turns to be SUSCEPTIBLE
            # and, if you're lucky, you may gain resistance
            self.state = State.SUSCEPTIBLE
            self.try_gain_resistance()
        else:
            # otherwise, if you can't remove the infection
            # put again your state to "INFECTED"
            self.state = State.INFECTED

    def virus_scan(self):
        # Decide, according to virus_check_frequency, if it's time to make a virus scan
        # NB: a virus scan just means "check if you are infected"
        if random.uniform(0, 1) <= self.virus_check_frequency:
            # so, if it's time to do a virus_scan and you understand you got infected..
            # ...try to remove infection!
            if self.state == State.INFECTED:
                self.try_remove_infection()

    def step(self):
        # Check che suggested Agent Flow Chart...
        # if this PC is infected try to infect your neighbors
        if self.state == State.INFECTED:
            self.try_to_infect_neighbors()

        # after the above step, always try to make a virus_scan
        # at every execution step
        self.virus_scan()
