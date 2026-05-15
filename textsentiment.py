from transformers import pipeline

text_emotion_model = pipeline(
    "text-classification",
    model="j-hartmann/emotion-english-distilroberta-base",
    top_k=None
)

def analyze_text_sentiment(text):
    if text is None or text.strip() == "":
        return {
            "label": "neutral",
            "score": 0,
            "positive_score": 0,
            "negative_score": 0,
            "suboptimal_score": 0,
            "text_score": 0,
            "joy": 0,
            "neutral": 0,
            "sadness": 0,
            "anger": 0,
            "fear": 0,
            "disgust": 0,
            "surprise": 0
        }

    results = text_emotion_model(text)[0]

    emotion_scores = {
        item["label"]: item["score"]
        for item in results
    }

    joy = emotion_scores.get("joy", 0)
    neutral = emotion_scores.get("neutral", 0)
    anger = emotion_scores.get("anger", 0)
    sadness = emotion_scores.get("sadness", 0)
    fear = emotion_scores.get("fear", 0)
    disgust = emotion_scores.get("disgust", 0)
    surprise = emotion_scores.get("surprise", 0)

    positive_score = joy + neutral * 0.3

    negative_score = (
        anger +
        sadness +
        fear +
        disgust +
        surprise * 0.3
    )

    top_emotion = max(emotion_scores, key=emotion_scores.get)
    top_emotion_score = emotion_scores[top_emotion]
    suboptimal_score = negative_score / (positive_score + negative_score)*top_emotion_score
    
    

    return {
        "label": top_emotion,
        "top_emotion_score": round(top_emotion_score, 3),
        "positive_score": round(positive_score, 3),
        "negative_score": round(negative_score, 3),
        "suboptimal_score": round(suboptimal_score, 3),
        "text_score": round(suboptimal_score, 3),
        "joy": round(joy * 100, 2),
        "neutral": round(neutral * 100, 2),
        "sadness": round(sadness * 100, 2),
        "anger": round(anger * 100, 2),
        "fear": round(fear * 100, 2),
        "disgust": round(disgust * 100, 2),
        "surprise": round(surprise * 100, 2)
    }