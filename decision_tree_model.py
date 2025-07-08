import pandas as pd
import numpy as np
from collections import Counter

#Computing entropy
def entropy(labels):
    total = len(labels)
    counts = Counter(labels)
    probabilities = [count / total for count in counts.values()]
    return -sum(p * np.log2(p) for p in probabilities if p > 0)

#Spliting dataset based on an attribute
def split_data(data, feature, threshold):
    left = data[data[feature] <= threshold]
    right = data[data[feature] > threshold]
    
    if len(left) == 0 or len(right) == 0:
        return None, None  # Prevents invalid splits
    
    return left, right

#Computing information gain
def information_gain(data, feature, threshold):
    total_entropy = entropy(data['label'].values)
    left, right = split_data(data, feature, threshold)
    
    if left is None or right is None:
        return 0  # No valid split
    
    weight_left = len(left) / len(data)
    weight_right = len(right) / len(data)
    
    gain = total_entropy - (weight_left * entropy(left['label'].values) + weight_right * entropy(right['label'].values))
    return gain


""" Finding the best feature to split on

- Avoids splitting on exact values (which can overfit).
- Reduces the number of splits tested, making it faster. """
def find_best_split(data, features):
    best_gain = 0
    best_feature = None
    best_threshold = None
    
    for feature in features:
        sorted_values = sorted(data[feature].unique())
        thresholds = [(sorted_values[i] + sorted_values[i+1]) / 2 for i in range(len(sorted_values) - 1)]
        
        for threshold in thresholds:
            gain = information_gain(data, feature, threshold)
            if gain > best_gain:
                best_gain = gain
                best_feature = feature
                best_threshold = threshold
    
    return best_feature, best_threshold

def find_best_two_splits(data, features):
    best_gain = 0
    best_feature = None
    best_thresholds = (None, None)
    
    for feature in features:
        sorted_values = sorted(data[feature].unique())
        thresholds = [(sorted_values[i] + sorted_values[i+1]) / 2 for i in range(len(sorted_values) - 1)]
        
        # Try all pairs of thresholds
        for i in range(len(thresholds)):
            for j in range(i + 1, len(thresholds)):
                t1 = thresholds[i]
                t2 = thresholds[j]
                
                # Split into 3 parts: <= t1, (t1, t2], > t2
                left = data[data[feature] <= t1]
                middle = data[(data[feature] > t1) & (data[feature] <= t2)]
                right = data[data[feature] > t2]
                
                # Calculate weighted entropy
                total_entropy = entropy(data['label'].values)
                weight_left = len(left) / len(data)
                weight_middle = len(middle) / len(data)
                weight_right = len(right) / len(data)
                
                weighted_entropy = (
                    weight_left * entropy(left['label'].values) +
                    weight_middle * entropy(middle['label'].values) +
                    weight_right * entropy(right['label'].values)
                )
                
                gain = total_entropy - weighted_entropy
                
                if gain > best_gain:
                    best_gain = gain
                    best_feature = feature
                    best_thresholds = (t1, t2)
    
    return best_feature, best_thresholds

""" Building of the decision tree recursively

Preventing Overfitting in build_tree

- Max depth: Limit recursion to prevent overly deep trees.

- Min samples per split: Stop splitting when a node has too few samples. """

MAX_DEPTH = 10  # Example limit
MIN_SAMPLES = 5  # Minimum number of samples in a node

def build_tree_two_thresholds(data, features, depth=0):
    labels = data['label']

    # Stopping conditions
    if len(set(labels)) == 1 or len(features) == 0 or len(data) < MIN_SAMPLES or depth >= MAX_DEPTH:
        return Counter(labels).most_common(1)[0][0]

    # Use the two-threshold function here
    best_feature, (t1, t2) = find_best_two_splits(data, features)
    
    # If no good split is found, return majority label
    if best_feature is None or t1 is None or t2 is None:
        return Counter(labels).most_common(1)[0][0]

    # Split into 3 parts
    left_data = data[data[best_feature] <= t1]
    middle_data = data[(data[best_feature] > t1) & (data[best_feature] <= t2)]
    right_data = data[data[best_feature] > t2]

    # (Optional: Stop if one of the splits is empty)
    if len(left_data) == 0 or len(middle_data) == 0 or len(right_data) == 0:
        return Counter(labels).most_common(1)[0][0]

    # Continue building the tree
    new_features = [f for f in features if f != best_feature]

    tree = {best_feature: {}}
    tree[best_feature]['<= ' + str(t1)] = build_tree_two_thresholds(left_data, new_features, depth + 1)
    tree[best_feature]['(' + str(t1) + ', ' + str(t2) + ']'] = build_tree_two_thresholds(middle_data, new_features, depth + 1)
    tree[best_feature]['> ' + str(t2)] = build_tree_two_thresholds(right_data, new_features, depth + 1)

    return tree



#Classification of new examples
def classify(tree, row):
    if not isinstance(tree, dict):
        return tree
    feature = next(iter(tree))
    sub_tree = tree[feature]
    
    for key in sub_tree.keys():
        if key.startswith('<='):
            # Example: '<= 1.75'
            threshold = float(key.split('<= ')[1])
            if row[feature] <= threshold:
                return classify(sub_tree[key], row)
        elif key.startswith('('):
            # Example: '(1.75, 3.0]'
            # First remove parentheses and brackets
            clean = key.strip('()[]')
            t1, t2 = clean.split(', ')
            t1 = float(t1)
            t2 = float(t2)
            if t1 < row[feature] <= t2:
                return classify(sub_tree[key], row)
        elif key.startswith('>'):
            # Example: '> 3.0'
            threshold = float(key.split('> ')[1].strip(']'))  # Strip extra bracket if any
            if row[feature] > threshold:
                return classify(sub_tree[key], row)
    
    # fallback in case no condition matched
    return None


def evaluate(tree, test_data):
    correct = 0
    for _, row in test_data.iterrows():
        if classify(tree, row) == row['label']:
            correct += 1
    return correct / len(test_data)

def train_tree(difficulty):
    dataset_map = {
        "easy": "mcts_dataset_easy.csv",
        "medium": "mcts_dataset_medium.csv",
        "hard": "mcts_dataset_hard.csv"
    }

    col_names = [f"cell_{i}" for i in range(42)] + ["label"]

    

    df = pd.read_csv(dataset_map[difficulty], header=None, names=col_names)

    mapping = {" ": 0, "x": 1, "o": 2}
    for i in range(42):
        col = f"cell_{i}"
        df[col] = df[col].apply(lambda x: mapping.get(x, 0))



    features = [f"cell_{i}" for i in range(42)]
    tree = build_tree_two_thresholds(df, features)

    return tree

def predict_from_tree(tree, board):
    mapping = {" ": 0, "x": 1, "o": 2}
    flat_board = [mapping.get(cell.strip(), 0) for row in board for cell in row]
    example = {f"cell_{i}": flat_board[i] for i in range(42)}
    return classify(tree, example)

