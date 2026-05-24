# LEGACY: This file has been replaced by sceneControl.py
# Kept for reference only - all functionality is now in sceneControl.py

    send_ws({
        "type": "text",
        "transcript": transcript,
        "label": text_result["label"],
        "joy": text_result.get("joy", 0),
        "sadness": text_result.get("sadness", 0),
        "anger": text_result.get("anger", 0),
        "fear": text_result.get("fear", 0),
        "surprise": text_result.get("surprise", 0),
        "neutral": text_result.get("neutral", 0),
        "disgust": text_result.get("disgust", 0),
        "score": text_result["text_score"]
    })

    # Combine scores
    question_score = calculate_final_score(
        face_score=face_score,
        voice_score=voice_score,
        text_score=text_score
    )

    question_result = {
        "question_number": question_number,
        "transcript": transcript,

        "valence": round(face_values["valence"], 2),
        "thinking": round(face_values["thinking"], 2),
        "arousal": round(face_values["arousal"], 2),
        "anxious": round(face_values["anxious"], 2),

        "face_score": round(face_score, 2),
        "voice_score": round(voice_score, 2),
        "text_score": round(text_score, 2),

        **text_result,
        **question_score
    }

    send_ws({
        "type": "state",
        "question": question_number,
        "status": "answering"
    })

    print("")
    print("---------- QUESTION RESULT ----------")
    print("Transcript:", transcript)
    print("Face Score:", round(face_score, 2))
    print("Voice Score:", round(voice_score, 2))
    print("Text Score:", round(text_score, 2))
    print("Final:", question_score)

    return question_result