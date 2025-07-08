import random

quiz_questions = [
    {
        "question": "What planet is known as the Red Planet?",
        "options": ["A) Venus", "B) Mars", "C) Jupiter", "D) Saturn"],
        "answer": "b"
    },
    {
        "question": "What does H2O stand for?",
        "options": ["A) Oxygen", "B) Hydrogen", "C) Water", "D) Salt"],
        "answer": "c"
    },
    {
        "question": "Which is the fastest land animal?",
        "options": ["A) Cheetah", "B) Lion", "C) Tiger", "D) Gazelle"],
        "answer": "a"
    },
    # Add more questions...
]

def get_random_quiz():
    return random.choice(quiz_questions)
