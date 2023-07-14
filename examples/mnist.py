import os
import time
import experimenthq as ex
from sklearn.datasets import fetch_openml
from sklearn.model_selection import train_test_split, ParameterGrid
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score

# Load MNIST dataset
mnist = fetch_openml("mnist_784", version=1)
X = mnist.data
y = mnist.target

# Split the dataset into training and test sets
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Define hyperparameters to search
hyperparameters = {"n_neighbors": [3, 5, 7], "weights": ["uniform", "distance"]}

# Create a KNN model
knn = KNeighborsClassifier()

# Manually iterate over all combinations of hyperparameters
for params in ParameterGrid(hyperparameters):
    # Start a new experiment
    experiment = ex.Experiment(
        project="KNN on MNIST Dataset",
        api_key=os.environ["EXPERIMENT_HQ_API_KEY"],
    )

    # Log the hyperparameters
    experiment.log_parameter("n_neighbors", params["n_neighbors"], "number")
    experiment.log_parameter("weights", params["weights"], "select")

    # Set the parameters for the model
    knn.set_params(**params)

    # Fit the model and predict
    knn.fit(X_train, y_train)
    y_pred = knn.predict(X_test)

    # Calculate and log the accuracy
    accuracy = accuracy_score(y_test, y_pred)
    experiment.log_parameter("accuracy", accuracy, "number")

    time.sleep(15)

    print(f"Test Accuracy with {params}: {accuracy}")
