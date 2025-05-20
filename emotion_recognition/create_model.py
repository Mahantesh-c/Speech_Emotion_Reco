"""
Script to train a real emotion recognition model using RAVDESS, EMOVO, and TESS datasets.
Extracts features from each audio file and saves a trained model to model/emotion_model.pkl.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pickle
import numpy as np
from tqdm import tqdm
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from sklearn.preprocessing import StandardScaler
from sklearn.utils.class_weight import compute_class_weight
from sklearn.model_selection import GridSearchCV
from collections import Counter

from django.conf import settings
from emotion_recognition.audio_processor import process_audio_file

# Emotion mapping for each dataset (update as needed)
EMOTION_MAP = {
    'angry': ['angry', 'anger'],
    'disgust': ['disgust'],
    'fear': ['fear'],
    'happy': ['happy', 'happiness'],
    'neutral': ['neutral', 'neutrality'],
    'sad': ['sad', 'sadness'],
    'surprised': ['surprised', 'surprise']
}
EMOTIONS = list(EMOTION_MAP.keys())

# Helper to map a filename or folder to a standard emotion label
def get_emotion_from_path(path):
    lower = path.lower()
    for std, aliases in EMOTION_MAP.items():
        for alias in aliases:
            if alias in lower:
                return std
    return None

def collect_data(dataset_dirs):
    X, y = [], []
    for dataset_dir in dataset_dirs:
        for root, _, files in os.walk(dataset_dir):
            for file in files:
                if file.lower().endswith('.wav'):
                    file_path = os.path.join(root, file)
                    emotion = get_emotion_from_path(file_path)
                    if emotion is None:
                        continue
                    try:
                        features = process_audio_file(file_path)
                        if features is not None and len(features) == 38:
                            X.append(features)
                            y.append(EMOTIONS.index(emotion))
                    except Exception as e:
                        print(f"Error processing {file_path}: {e}")
    return np.array(X), np.array(y)

def main():
    # Paths to datasets
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dataset_dirs = [
        os.path.join(base, 'datasets', 'ravdess'),
        os.path.join(base, 'datasets', 'emovo'),
        os.path.join(base, 'datasets', 'tess'),
    ]
    print("Collecting data from datasets...")
    X, y = collect_data(dataset_dirs)
    print(f"Collected {len(X)} samples.")
    if len(X) == 0:
        print("No data found. Exiting.")
        return

    # Feature normalization
    scaler = StandardScaler()
    X = scaler.fit_transform(X)

    # Compute class weights for imbalanced data
    class_weights = compute_class_weight('balanced', classes=np.unique(y), y=y)
    class_weight_dict = {i: w for i, w in enumerate(class_weights)}

    # Fix for small datasets: check if stratified split is possible
    class_counts = Counter(y)
    min_class_count = min(class_counts.values())
    n_classes = len(class_counts)
    test_size = max(n_classes, int(0.15 * len(X)))
    if min_class_count < 2 or len(X) < n_classes * 2:
        print("Not enough samples for stratified split, using random split without stratify.")
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=42, stratify=None)
    else:
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=42, stratify=y)

    # Hyperparameter tuning (optional, can be commented for speed)
    # param_grid = {
    #     'n_estimators': [100, 200],
    #     'max_depth': [15, 20, 30],
    #     'min_samples_split': [2, 5],
    #     'min_samples_leaf': [1, 2]
    # }
    # grid = GridSearchCV(RandomForestClassifier(class_weight=class_weight_dict, random_state=42), param_grid, cv=3, n_jobs=-1)
    # grid.fit(X_train, y_train)
    # model = grid.best_estimator_
    # print(f"Best params: {grid.best_params_}")

    print("Training RandomForestClassifier...")
    model = RandomForestClassifier(n_estimators=200, max_depth=30, min_samples_split=2, min_samples_leaf=1, class_weight=class_weight_dict, random_state=42)
    model.fit(X_train, y_train)

    # Evaluate
    y_pred = model.predict(X_test)
    unique_labels = np.unique(np.concatenate([y_test, y_pred]))
    print(classification_report(y_test, y_pred, labels=unique_labels, target_names=[EMOTIONS[i] for i in unique_labels]))
    if hasattr(model, 'feature_importances_'):
        print("Feature importances:", model.feature_importances_)

    # Save model and scaler
    model_dir = os.path.join(base, 'model')
    os.makedirs(model_dir, exist_ok=True)
    model_path = os.path.join(model_dir, 'emotion_model.pkl')
    scaler_path = os.path.join(model_dir, 'scaler.pkl')
    with open(model_path, 'wb') as f:
        pickle.dump(model, f)
    with open(scaler_path, 'wb') as f:
        pickle.dump(scaler, f)
    print(f"Model saved to {model_path}")
    print(f"Scaler saved to {scaler_path}")

if __name__ == "__main__":
    main()
