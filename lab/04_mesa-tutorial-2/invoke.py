from model.money_model import MoneyModel
import numpy as np
from matplotlib import pyplot as plt

def do():
    model = MoneyModel(50, 10, 10)
    for i in range(20):
        model.step()

    agent_counts = np.zeros((model.grid.width, model.grid.height))
    for cell in model.grid.coord_iter():
        cell_content, x, y = cell
        agent_count = len(cell_content)
        agent_counts[x][y] = agent_count
    plt.imshow(agent_counts, interpolation='nearest')
    plt.colorbar()

do()