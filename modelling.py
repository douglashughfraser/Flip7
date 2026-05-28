import csv
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import TensorDataset, DataLoader
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score, accuracy_score, classification_report

import random

N_BITS = 22  # number of original hand columns

# Original column names in left-to-right order (MSB first)
HAND_COLS = [
    "#12","#11","#10","#9","#8","#7","#6","#5",
    "#4","#3","#2","#1","#0",
    "SC","Fr","F3","+2","+4","+6","+8","+10","X2",
]

def graph(counts):
    # Exclude busts
    counts = counts[counts.index > 0] 

    plt.figure(figsize=(12, 5))
    plt.bar(counts.index, counts.values, width=0.9, color="steelblue")
    plt.xlabel("Hand score")
    plt.ylabel("Count")
    plt.title("Score distribution")
    plt.tight_layout()
    plt.show()

"""
Claude-generated helper
load_compressed.py  –  Load the compressed CSV for model training.

Replaces the original snippet:
    data = pd.read_csv(file)
    data = data.sort_values("Result", ascending=False)

The "Hand" integer is expanded back into 22 individual bit-columns so the
rest of your pipeline sees the same feature shape as before.
"""
def load(file: str) -> pd.DataFrame:
    data = pd.read_csv(file)
 
    # Expand the Hand integer back into individual bit columns via bitwise shift
    hand_ints = data["Hand"].values.astype(np.int32)
    bits = np.array([
        [(v >> (N_BITS - 1 - i)) & 1 for i in range(N_BITS)]
        for v in hand_ints
    ])
 
    bit_df = pd.DataFrame(bits, columns=HAND_COLS, index=data.index)
    data = pd.concat([bit_df, data[["Result"]]], axis=1)
 
    return data


def train_linear_regression_model(file = "plays.csv"):

    data = load(file)

    data = data.sort_values("Result", ascending=False)

    data = data.loc[data["Result"]>0]

    #graph(data["Result"].value_counts())

    # Create tensore from dataframe
    tensor = torch.from_numpy(data.values)

    # Split into features (cards) and target (Result)
    X = data.drop(columns=["Result"])
    y = data["Result"]
    feature_columns = X.columns.tolist()

    # 80/20 train/test split into dataframes
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Create feature tensors
    X_train = torch.tensor(X_train.values, dtype=torch.float32)
    X_test  = torch.tensor(X_test.values, dtype=torch.float32)

    # Create test tensors
    y_train = torch.tensor(y_train.values, dtype=torch.float32).reshape(-1, 1)
    y_test  = torch.tensor(y_test.values, dtype=torch.float32).reshape(-1, 1)

    # 
    train_dataset = TensorDataset(X_train, y_train)
    train_loader = DataLoader(train_dataset, batch_size=4096, shuffle=True)

    model = nn.Sequential(
        nn.Linear(X.shape[1], 64),
        nn.ReLU(),
        nn.Linear(64, 32),
        nn.ReLU(),
        nn.Linear(32, 1)
    )

    # Batch training
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)

    epochs = 20

    for epoch in range(epochs):
        total_loss = 0

        for batch_X, batch_y in train_loader:
            predictions = model(batch_X)

            loss = criterion(predictions, batch_y)

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            total_loss += loss.item()

        print(f"Epoch {epoch+1}: {total_loss:.4f}")

    print(f'Num result = {data["Result"].count()}')
    print(f'Maximum result = {data["Result"].max()}')
    print(f'Median result = {data["Result"].median()}')
    print(f'Mean result = {data["Result"].mean()}')
    print(f'Std dev result = {data["Result"].std()}')
    print(f'Mode result = {data["Result"].mode()}')
    print(f'Results by value = \n{data["Result"].value_counts()}')

    with torch.no_grad():
        predictions = model(X_test)
        test_loss = criterion(predictions, y_test)

        print("Test loss:", test_loss.item())

    torch.save({
        "input_size": X.shape[1],
        "feature_columns": feature_columns,
        "state_dict": model.state_dict()
    }, "./linear_regression_model_nn.pth")

    model.eval()

    return model, X_test, y_test, feature_columns

def train_binary_classification_model(file = "plays.csv"):
    data = load(file)
    data = data.sort_values("Result", ascending=False)

    data = pd.read_csv("plays.csv")
    data = data.sort_values("Result", ascending=False)

    #graph(data["Result"].value_counts())

    # Create tensore from dataframe
    tensor = torch.from_numpy(data.values)

    # Split into features (cards) and target (Result)
    X = data.drop(columns=["Result"])
    y = (data["Result"] == 0).astype(int)
    feature_columns = X.columns.tolist()

    # 80/20 train/test split into dataframes
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Create feature tensors
    X_train = torch.tensor(X_train.values, dtype=torch.float32)
    X_test  = torch.tensor(X_test.values, dtype=torch.float32)

    # Create test tensors
    y_train = torch.tensor(y_train.values, dtype=torch.float32).reshape(-1, 1)
    y_test  = torch.tensor(y_test.values, dtype=torch.float32).reshape(-1, 1)

    # 
    train_dataset = TensorDataset(X_train, y_train)
    train_loader = DataLoader(train_dataset, batch_size=4096, shuffle=True)

    model = nn.Sequential(
        nn.Linear(X.shape[1], 64),
        nn.ReLU(),
        nn.Linear(64, 32),
        nn.ReLU(),
        nn.Linear(32, 1),
        nn.Sigmoid()
    )

    # Batch training
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)

    epochs = 20

    for epoch in range(epochs):
        total_loss = 0

        for batch_X, batch_y in train_loader:
            predictions = model(batch_X)

            loss = criterion(predictions, batch_y)

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            total_loss += loss.item()

        print(f"Epoch {epoch+1}: {total_loss:.4f}")

    print(f'Num result = {data["Result"].count()}')
    print(f'Maximum result = {data["Result"].max()}')
    print(f'Median result = {data["Result"].median()}')
    print(f'Mean result = {data["Result"].mean()}')
    print(f'Std dev result = {data["Result"].std()}')
    print(f'Mode result = {data["Result"].mode()}')
    print(f'Results by value = \n{data["Result"].value_counts()}')

    with torch.no_grad():
        bust_chance = model(X_test)
        predictions= (bust_chance >= 0.5).float()

        print(f"Accuracy: {accuracy_score(y_test, predictions):.3f}")
        print(classification_report(y_test, predictions, target_names=["Non-zero", "Zero"]))

    torch.save({
        "input_size": X.shape[1],
        "feature_columns": feature_columns,
        "state_dict": model.state_dict()
    }, "./binary_classification_model_nn.pth")

    model.eval()

    return model, X_test, y_test, feature_columns

def main():

    model, X_test, y_test, feature_columns = train_binary_classification_model("plays.csv")

    # Evaluate
    model.eval()

    with torch.no_grad():
        y_pred = model(X_test)
    print(f"R²:   {r2_score(y_test, y_pred):.3f}")
    print(f"RMSE: {np.sqrt(mean_squared_error(y_test, y_pred)):.3f}")

    for tester in range(0,100):
        sample_no = random.randint(0, len(X_test))

        sample = X_test[sample_no].unsqueeze(0)

        with torch.no_grad():
            pred = model(sample)

        hand = {
            feature_columns[i]: int(X_test[sample_no][i].item())
            for i in range(len(feature_columns))
            if X_test[sample_no][i].item() != 0
        }

        print(f"Hand: {hand}")
        print(f"\tPredicted: {pred.item()} \tActual: {y_test[sample_no].item()}")

        sample = X_test[sample_no].unsqueeze(0)

        with torch.no_grad():
            pred = model(sample)

        hand = {
            feature_columns[i]: int(X_test[sample_no][i].item())
            for i in range(len(feature_columns))
            if X_test[sample_no][i].item() != 0
        }

        print(f"Hand: {hand}")
        print(f"\tPredicted: {pred.item()} \tActual: {y_test[sample_no].item()}")


if __name__=="__main__":
    main()