import code  # code.interact(local=dict(globals(), **locals()))

from mesa.batchrunner import BatchRunner

from MoneyModel import MoneyModel, dataCollectorReporter

fixed_params = {
    "width": 10,
    "height": 10
}

variable_params = {"N": range(10, 100, 10)}

batch_run = BatchRunner(
    MoneyModel,
    variable_params,
    fixed_params,
    iterations=5,
    max_steps=20,
    model_reporters={"allData": dataCollectorReporter}
)

batch_run.run_all()

code.interact(local=dict(globals(), **locals()))

# here "dataCollectorReporter" passed as model reporter, so we get
# data back using get_MODEL_vars_dataframe()
alldata = batch_run.get_model_vars_dataframe()

# Inside you find a datacollector object for each run
# Let's get the first run datacollector
run0data = alldata[alldata.Run == 0].allData.loc[0]

# Within run0data you have the usual model data (gini for each step)
run0Mdata = run0data.get_model_vars_dataframe()

# And also the wealth of each agent for each step
run0Adata = run0data.get_agent_vars_dataframe()

# So you have all data of each step of each run! Smile! :)
