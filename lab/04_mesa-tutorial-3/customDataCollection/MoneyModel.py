from mesa import Model
from mesa.datacollection import DataCollector
from mesa.space import MultiGrid
from mesa.time import RandomActivation

from MoneyAgent import MoneyAgent

'''
Convenience function to report a full datacollector object
'''


def dataCollectorReporter(model):
    return model.datacollector


def agent_wealth(agent):
    return agent.wealth


def compute_gini(model):
    agent_wealths = [agent.wealth for agent in model.schedule.agents]
    x = sorted(agent_wealths)
    N = model.num_agents
    B = sum(xi * (N - i) for i, xi in enumerate(x)) / (N * sum(x))
    return (1 + (1 / N) - 2 * B)


class MoneyModel(Model):
    """A model with some number of agents."""

    def __init__(self, N, width, height):
        self.num_agents = N
        self.grid = MultiGrid(width, height, torus=True)
        self.schedule = RandomActivation(self)
        self.steps = 0
        self.running = True

        # Create agents
        for i in range(self.num_agents):
            a = MoneyAgent(i, self)
            self.schedule.add(a)

            # Add the agent to a random grid cell
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(a, (x, y))

        # Add Data Collector
        self.datacollector = DataCollector(
            # `compute_gini` defined above
            model_reporters={"Gini": compute_gini},
            agent_reporters={"Wealth": agent_wealth})

    def step(self):
        # code.interact(local=dict(globals(), **locals()))
        '''Collect data only at even steps'''
        #if self.steps % 2 == 0:
        self.datacollector.collect(self)
        self.schedule.step()
        self.steps += 1
