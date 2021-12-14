import matplotlib.pyplot as plt

from model.money_model import MoneyModel

model = MoneyModel(10)
for i in range(10):
    model.step()

plt.show()

# For a jupyter notebook add the following line:
# %matplotlib inline
# The below is needed for both notebooks and scripts

agent_wealth = [a.wealth for a in model.schedule.agents]
plt.hist(agent_wealth)
