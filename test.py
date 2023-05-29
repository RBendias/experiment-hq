import experimenthq as ex

experiment = ex.Experiment(
    name="Lukas First Experiment",
    project="foobar",
    api_key="2904e63c-eab8-4c3a-ba42-c5566d4fa229",
)

experiment.log_parameter("accuracy", 0.85)
experiment.log_parameter("loss", 0.05, notion_type="number")
