import os
import pickle
import logging
from .features import extract_features, get_topic, auto_label

logger = logging.getLogger(__name__)

MODEL_PATH = os.path.join(os.path.dirname(__file__), 'model.pkl')
DIFFICULTY_LABELS = {0: 'easy', 1: 'medium', 2: 'hard'}

_model = None


def load_model():
    global _model
    if _model is None:
        if os.path.exists(MODEL_PATH):
            with open(MODEL_PATH, 'rb') as f:
                _model = pickle.load(f)
        else:
            logger.warning("Model not found. Run: python manage.py train_difficulty_model")
    return _model


def predict_difficulty(question_text, option_a='', option_b='', option_c='', option_d=''):
    model = load_model()
    if model is None:
        return DIFFICULTY_LABELS[auto_label(question_text)]
    try:
        import numpy as np
        features = extract_features(question_text, option_a, option_b, option_c, option_d)
        prediction = model.predict(np.array([features]))[0]
        return DIFFICULTY_LABELS[int(prediction)]
    except Exception as e:
        logger.error("Prediction error: %s", e)
        return DIFFICULTY_LABELS[auto_label(question_text)]


def predict_topic(question_text, option_a='', option_b='', option_c='', option_d=''):
    """
    Assign a topic using the multi-signal engine. Passing the answer options
    lets the engine use its strongest signal (the format of the options),
    and the engine reads its keyword knowledge base from the database
    (Supabase) so topics can be edited without changing code.
    """
    return get_topic(question_text, option_a, option_b, option_c, option_d)
