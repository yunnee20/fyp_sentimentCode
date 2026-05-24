# Sentiment score calculation module
# Combines individual modality scores (facial, vocal, textual) into
# final authenticity assessment using weighted averaging

def calculate_final_score(face_score, voice_score, text_score):
    """Calculate final authenticity score from individual modalities.
    
    Weighting: 50% facial expression, 20% voice prosody, 30% text sentiment
    
    Args:
        face_score: Facial emotion score (0-100)
        voice_score: Voice energy/pitch score (0-100)
        text_score: Text sentiment score (0-100)
        
    Returns:
        Dictionary with component scores, final score, authenticity, and label
    """
    final_score = (
        0.5 * face_score +
        0.2 * voice_score +
        0.3 * text_score
    )

    final_score = max(0, min(100, final_score))
    authenticity = 100 - final_score

    if final_score >= 50:
        label = "Optimal"
    else:
        label = "Suboptimal"

    return {
        "face_score": round(face_score, 2),
        "voice_score": round(voice_score, 2),
        "text_score": round(text_score, 2),
        "final_score": round(final_score, 2),
        "authenticity": round(authenticity, 2),
        "label": label
    }


def calculate_total_score(question_results):
    if not question_results:
        return None

    avg_face = sum(q["face_score"] for q in question_results) / len(question_results)
    avg_voice = sum(q["voice_score"] for q in question_results) / len(question_results)
    avg_text = sum(q["text_score"] for q in question_results) / len(question_results)

    return calculate_final_score(avg_face, avg_voice, avg_text)