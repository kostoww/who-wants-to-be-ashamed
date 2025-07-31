from sqlalchemy.orm import Session
from sqlalchemy import func
from . import models, llm_service

def play_turn(db: Session, agent_name: str, system_prompt: str, skill_level: float):
    """
    Simulates a turn for a specific AI agent persona.
    1. Selects a random question from the database.
    2. Uses an LLM with a specific system prompt and skill level to generate a structured answer.
    3. Verifies if the generated answer is correct.
    """
    # 1. Select a random question from the DB
    random_question = db.query(models.JeopardyQuestion).order_by(func.random()).first()
    if not random_question:
        return {
            "agent_name": agent_name,
            "question": "Could not find a question in the database.",
            "ai_answer": "",
            "ai_explanation": "The database seems to be empty.",
            "is_correct": False
        }

    ai_answer, ai_explanation = llm_service.get_structured_answer_from_llm(
        system_prompt=system_prompt,
        question=random_question.question,
        skill_level=skill_level  # Pass the skill level here
    )

    is_correct, _ = llm_service.verify_answer_with_llm(
        question=random_question.question,
        correct_answer=random_question.answer,
        user_answer=ai_answer
    )

    return {
        "agent_name": agent_name,
        "question": random_question.question,
        "ai_answer": ai_answer,
        "ai_explanation": ai_explanation,
        "is_correct": is_correct
    }