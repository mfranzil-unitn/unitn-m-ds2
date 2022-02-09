import matplotlib
import matplotlib.pyplot as plt
import numpy as np

from model.money_model import MoneyModel

model = MoneyModel(50, 10, 10)
for i in range(200):
    model.step()

# code.interact(local=dict(globals(), **locals()))

# gini = model.datacollector.get_model_vars_dataframe()
# gini.plot()
#
# agent_wealth = model.datacollector.get_agent_vars_dataframe()
# agent_wealth.head()
#
# end_wealth = agent_wealth.xs(99, level="Step")["Wealth"]
# end_wealth.hist(bins=range(agent_wealth.Wealth.max()+1))
#
# one_agent_wealth = agent_wealth.xs(14, level="AgentID")
# one_agent_wealth.Wealth.plot()

matplotlib.use('TkAgg')

agent_counts = np.zeros((model.grid.width, model.grid.height))
for cell in model.grid.coord_iter():
    cell_content, x, y = cell
    agent_count = len(cell_content)
    agent_counts[x][y] = agent_count
plt.imshow(agent_counts, interpolation='nearest')
plt.colorbar()
plt.show()
