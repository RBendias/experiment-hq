import os
import experimenthq as ex
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score

# Load iris dataset
iris = load_iris()
X = iris.data
y = iris.target

# Split the dataset into training and test sets
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Define the experiment
experiment = ex.Experiment(
    project="KNN on Iris Dataset",
    api_key=os.environ["EXPERIMENT_HQ_API_KEY"],
)

# Hyperparameters
n_neighbors = 3
weights = "uniform"

# Log hyperparameters
experiment.log_parameter("n_neighbors", n_neighbors)
experiment.log_parameter("weights", weights)

# Train the model
knn = KNeighborsClassifier(n_neighbors=n_neighbors, weights=weights)
knn.fit(X_train, y_train)

# Predict on the test set and calculate accuracy
y_pred = knn.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)

# Log the accuracy
experiment.log_parameter("accuracy", accuracy)

print(f"Test Accuracy: {accuracy}")
