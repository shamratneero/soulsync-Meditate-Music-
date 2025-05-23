def detect_mood_from_text(user_input):
    user_input = user_input.lower()

    if "sad" in user_input or "depressed" in user_input:
        return "sad"
    elif "anxious" in user_input or "stressed" in user_input:
        return "lost"
    elif "excited" in user_input or "energetic" in user_input:
        return "focused"
    elif "tired" in user_input or "sleepy" in user_input:
        return "relaxed"
    elif "happy" in user_input or "joyful" in user_input:
        return "happy"
    else:
        return "calm"  # Default mood if no keyword matches
