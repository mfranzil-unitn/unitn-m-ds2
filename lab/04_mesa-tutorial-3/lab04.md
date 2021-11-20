# OUTLINE LAB 4 - MESA Visualization + SIR Exercise


1) Add a Visualization to our Money Model
- https://mesa.readthedocs.io/en/stable/tutorials/adv_tutorial.html


2) Short further tutorial with few more visualization tricks
https://towardsdatascience.com/introduction-to-mesa-agent-based-modeling-in-python-bcb0596e1c9a


3) MESA SIR exercise




### Few missing Notes from the last time (BatchRunner)


<<Note that by default, the reporters only collect data at the end of the run. To get step by step data, simply have a reporter store the model’s entire DataCollector object.>>
- https://mesa.readthedocs.io/en/stable/apis/batchrunner.html
->  show how to report a collector to get all steps data


CUSTOMIZE “RATE” OF DATA COLLECTION


- show how to decide for which steps to collect data, adding 'steps' counter to model
 and using it to control whether to collect data at a given step or not
NB: we can also write data to disk if we want to customize post-processing, e.g., prefer to use R or Matlab instead of Python
* https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_csv.html




### Notes on visualization




Add a chain of "if agent type == Type 1 then generate one given portrayal, elif type2 then..."
so to define a custom drawing style for each kind of agent
https://mesa.readthedocs.io/en/stable/apis/visualization.html#modular-canvas-rendering


To understand the pieces required to instantiate a mesa surver
https://mesa.readthedocs.io/en/stable/apis/visualization.html#visualization.ModularVisualization.ModularServer


IDEM, pieces for setting up a chart module
https://mesa.readthedocs.io/en/stable/apis/visualization.html#chart-module




IDEM, for understanding how to setup a slider in the GUI for choosing/resetting model initialization params
https://mesa.readthedocs.io/en/stable/mesa.visualization.html?highlight=UserSettableParameter#mesa.visualization.UserParam.UserSettableParameter