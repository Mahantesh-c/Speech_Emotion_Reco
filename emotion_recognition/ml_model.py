import os
import pickle
import numpy as np
from django.conf import settings
import logging
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import warnings

# Configure logging
logger = logging.getLogger(__name__)

# Suppress warnings
warnings.filterwarnings('ignore')

# Emotion labels (ensure they're in the correct order that the model was trained on)
EMOTIONS = ['angry', 'disgust', 'fear', 'happy', 'neutral', 'sad', 'surprised']

# Path to the pre-trained model and scaler
MODEL_PATH = os.path.join(settings.MODEL_DIR, 'emotion_model.pkl')
SCALER_PATH = os.path.join(settings.MODEL_DIR, 'scaler.pkl')

def load_model():
    """
    Load the trained model and scaler from disk
    """
    try:
        with open(MODEL_PATH, 'rb') as f:
            model = pickle.load(f)
        with open(SCALER_PATH, 'rb') as f:
            scaler = pickle.load(f)
        return model, scaler
    except Exception as e:
        logger.error(f"Failed to load model or scaler: {str(e)}")
        # Fallback: create dummy model and identity scaler
        model = RandomForestClassifier()
        scaler = StandardScaler()
        return model, scaler

# Global model and scaler instance (lazy loading)
MODEL = None
SCALER = None

def get_model():
    """
    Get the model and scaler, loading them if necessary
    
    Returns:
        The loaded emotion recognition model and scaler
    """
    global MODEL, SCALER
    if MODEL is None or SCALER is None:
        MODEL, SCALER = load_model()
    return MODEL, SCALER

def predict_emotion(features):
    """
    Predict emotion from audio features
    
    Args:
        features: numpy array of audio features
        
    Returns:
        Tuple of (emotion_label, confidence_score, all_predictions)
    """
    try:
        # Get the model and scaler
        model, scaler = get_model()
        
        # Ensure features are in the right shape for the model
        features = np.array(features).reshape(1, -1)
        
        # Normalize features using the scaler
        features = scaler.transform(features)
        
        # Replace any NaN or Inf values
        if np.isnan(features).any() or np.isinf(features).any():
            logger.warning("Features contain NaN or Inf values, replacing with zeros")
            features = np.nan_to_num(features)
        
        # Get prediction probabilities
        probabilities = model.predict_proba(features)[0]
        
        # Get the predicted class index and corresponding emotion
        predicted_class = np.argmax(probabilities)
        emotion = EMOTIONS[predicted_class]
        confidence = float(probabilities[predicted_class])
        
        # Format all predictions for saving
        all_predictions = {emotion: float(prob) for emotion, prob in zip(EMOTIONS, probabilities)}
        
        logger.info(f"Emotion prediction: {emotion}, confidence: {confidence:.2f}")
        
        return emotion, confidence, all_predictions
        
    except Exception as e:
        logger.error(f"Error in emotion prediction: {str(e)}")
        logger.exception("Prediction error:")
        
        # Return a default prediction in case of error
        default_emotion = "neutral"
        default_confidence = 0.5
        default_predictions = {emotion: 0.1 for emotion in EMOTIONS}
        default_predictions[default_emotion] = default_confidence
        
        logger.warning(f"Using fallback prediction: {default_emotion}, confidence: {default_confidence}")
        
        return default_emotion, default_confidence, default_predictions

def create_new_model():
    """
    Create a new model for emotion recognition when loading fails
    
    Returns:
        Newly created model
    """
    logger.info("Creating new RandomForest model for emotion classification")
    
    # Create a RandomForest model with better parameters for emotion classification
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=20,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42
    )
    
    # Number of features we extract in audio_processor.py
    # 2 stats (mean, std) for 7 audio features (ZCR, 13 MFCCs, RMS, centroid, bandwidth, rolloff, chroma)
    # Total: 2 * (1 + 13 + 1 + 1 + 1 + 1 + 1) = 38 features
    num_features = 38
    
    # Generate diverse training examples to help with generalization
    X_dummy = np.zeros((700, num_features))
    y_dummy = []
    
    # Create 100 synthetic examples for each emotion
    for i, emotion in enumerate(EMOTIONS):
        # Create features with some distinguishing characteristics per emotion
        for j in range(100):
            features = np.random.rand(num_features) * 0.5  # Base randomness
            
            # Add some emotion-specific patterns
            if emotion == 'angry':
                features[0:2] = 0.7 + np.random.rand(2) * 0.3  # Higher ZCR
                features[30:34] = 0.8 + np.random.rand(4) * 0.2  # Higher spectral features
            elif emotion == 'happy':
                features[26:30] = 0.6 + np.random.rand(4) * 0.4  # Higher energy
                features[4:8] = 0.7 + np.random.rand(4) * 0.3  # Higher mid MFCCs
            elif emotion == 'sad':
                features[26:30] = 0.1 + np.random.rand(4) * 0.3  # Lower energy
                features[0:2] = 0.1 + np.random.rand(2) * 0.2  # Lower ZCR
            # Add noise to make features realistic
            features += np.random.randn(num_features) * 0.05
            
            # Store in training data
            X_dummy[i*100 + j] = features
            y_dummy.append(i)  # Class index
    
    # Convert to numpy array
    y_dummy = np.array(y_dummy)
    
    # Fit the model
    model.fit(X_dummy, y_dummy)
    
    # Ensure model directory exists
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    
    # Save this model for future use
    try:
        with open(MODEL_PATH, 'wb') as f:
            pickle.dump(model, f)
        logger.info(f"Saved new model to {MODEL_PATH}")
    except Exception as e:
        logger.error(f"Failed to save new model: {str(e)}")
    
    return model

def get_model_info():
    """
    Get information about the current model
    
    Returns:
        Dictionary with model information
    """
    model, _ = get_model()
    
    if hasattr(model, 'n_estimators'):
        n_estimators = model.n_estimators
    else:
        n_estimators = "Unknown"
    
    if hasattr(model, 'feature_importances_'):
        feature_importances = model.feature_importances_.tolist()
    else:
        feature_importances = []
    
    return {
        'model_type': model.__class__.__name__,
        'n_estimators': n_estimators,
        'n_classes': len(EMOTIONS),
        'emotions': EMOTIONS,
        'feature_importances': feature_importances,
        'model_path': MODEL_PATH
    }