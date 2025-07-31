import os
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


def get_answer_from_llm(question: str) -> str:
    """
    Uses an LLM to attempt to answer a given trivia question.
    """
    if not openai.api_key:
        return "AI agent is offline (OPENAI_API_KEY not set)."

    try:
        prompt = f"""
        You are a contestant in a trivia game. Answer the following question as concisely as possible.
        Question: "{question}"
        Answer:
        """

        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a knowledgeable trivia contestant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.0,
            max_tokens=50
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"AI agent experienced an error: {e}"