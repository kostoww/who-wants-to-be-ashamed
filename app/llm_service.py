import os
import random

import openai
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI()
api_key = os.getenv("OPENAI_API_KEY", "")

def verify_answer_with_llm(question: str, correct_answer: str, user_answer: str) -> (bool, str):
    """
    Verifies a user's answer using an LLM, allowing for semantic similarity and typos.
    """
    if not api_key:
        # Fallback to simple check if API key is not configured
        is_correct = correct_answer.strip().lower() == user_answer.strip().lower()
        ai_response = f"Offline check: The correct answer is '{correct_answer}'."
        return is_correct, ai_response

    try:
        prompt = f"""
        A user is playing a trivia game.
        The question was: "{question}"
        The correct answer is: "{correct_answer}"
        The user's answer was: "{user_answer}"

        Is the user's answer correct? Consider synonyms, slight misspellings, and context.
        For example, if the correct answer is "Copernicus" and the user answered "Copernics", it should be considered correct.
        If the question asks for a name and the user provides only the last name, it's usually correct.

        First, on a single line, write "true" if the answer is correct and "false" if it is not.
        Then, on a new line, provide a brief, friendly explanation for the user.
        Important: For the second line, Avoid to said  this is not the correct answer, or it is correct, i already know that i.e.
        DO NOT say "The correct answer is" or "You are wrong about this question" or "You are thinking/mistaking for something else".

        Example:
        true
        Yes, Nicolaus Copernicus is the correct answer!
        """

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful trivia judge."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.0,
            max_tokens=100
        )



        content = response.choices[0].message.content.strip()
        lines = content.split('\n', 1)

        is_correct_str = lines[0].strip().lower()
        ai_explanation = lines[1].strip() if len(lines) > 1 else "No explanation provided."

        is_correct = is_correct_str == 'true'
        return is_correct, ai_explanation

    except Exception as e:
        return False, f"Could not verify with AI due to an error: {e}"


def get_structured_answer_from_llm(system_prompt: str, question: str, skill_level: float) -> (str, str):
    """
    Uses an LLM with a specific persona to answer a trivia question and provide an explanation.
    Applies an agent-specific skill level to determine if the agent should be "confused".
    Returns a tuple of (ai_answer, ai_explanation).
    """
    if random.random() > skill_level:
        question = f"{question}\n\n(IMPORTANT! You are feeling very uncertain about this one. Your confidence is low. Make your response as mistake or a wild guess, which is again mistake based on your persona.)"

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question}
            ],
            temperature=0.7,
            max_tokens=150
        )

        content = response.choices[0].message.content.strip()
        lines = content.split('\n', 1)

        ai_answer = lines[0].strip()
        ai_explanation = lines[1].strip() if len(lines) > 1 else "..."

        return ai_answer, ai_explanation

    except Exception as e:
        return f"AI agent error", f"Could not get answer from AI due to an error: {e}"