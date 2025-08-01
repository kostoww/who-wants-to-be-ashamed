from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from collections import defaultdict

from . import models, schema
from .persistance import get_db
from . import llm_service
from . import agent
from .agent_instructions import AGENTS


router = APIRouter()

@router.get("/question/", response_model=schema.Question)
def get_random_question(round: str, value: str, db: Session = Depends(get_db)):
    """
    Returns a random question based on the provided Round and Value.
    """
    try:
        # Clean the value input, e.g., "$200" -> 200
        cleaned_value = int(value.replace('$', '').replace(',', ''))
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid value format. Please use a format like '$200'."
        )

    question = db.query(models.JeopardyQuestion).filter(
        models.JeopardyQuestion.round == round,
        models.JeopardyQuestion.value == cleaned_value
    ).order_by(func.random()).first() # func.random() is efficient for PostgreSQL

    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No questions found for round '{round}' and value '{value}'"
        )

    question.value = f"${question.value}"
    return question


@router.post("/verify-answer/", response_model=schema.VerifyAnswerResponse)
def verify_answer(request: schema.VerifyAnswerRequest, db: Session = Depends(get_db)):
    """
    Verifies if a user's answer is correct for a given question ID.
    Uses an LLM for more flexible answer checking.
    """
    question = db.query(models.JeopardyQuestion).filter(models.JeopardyQuestion.id == request.question_id).first()
    if not question:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found")

    is_correct, ai_response = llm_service.verify_answer_with_llm(
        question=question.question,
        correct_answer=question.answer,
        user_answer=request.user_answer
    )

    return schema.VerifyAnswerResponse(is_correct=is_correct, ai_response=ai_response)


@router.get("/gameboard/{round_name}")
def get_game_board(round_name: str, db: Session = Depends(get_db)):
    """
    Fetches a full, coherent game board for a given round from a single, random show.
    This is the primary endpoint for the new UI.
    """
    if round_name not in ["Jeopardy!", "Double Jeopardy!"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Round must be 'Jeopardy!' or 'Double Jeopardy!'"
        )

    complete_show_query = (
        db.query(models.JeopardyQuestion.show_number)
        .filter(models.JeopardyQuestion.round == round_name)
        .group_by(models.JeopardyQuestion.show_number)
        .having(func.count(func.distinct(models.JeopardyQuestion.category)) >= 6)
        .subquery()
    )

    random_show_row = db.query(complete_show_query).order_by(func.random()).first()

    if not random_show_row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No complete game boards could be found for the '{round_name}' round.")

    random_show_number = random_show_row[0]

    questions = (
        db.query(models.JeopardyQuestion)
        .filter(
            models.JeopardyQuestion.show_number == random_show_number,
            models.JeopardyQuestion.round == round_name
        )
        .order_by(models.JeopardyQuestion.category, models.JeopardyQuestion.value)
        .all()
    )

    categories = defaultdict(list)
    for q in questions:
        # We only care about questions that have a value
        if q.value and q.value > 0:
            categories[q.category].append({
                "question_id": q.id,
                "question": q.question,
                "answer": q.answer,
                "value": q.value
            })

    structured_board = {key: categories[key] for key in list(categories.keys())[:6]}

    return {
        "show_number": random_show_number,
        "round": round_name,
        "categories": structured_board
    }

@router.get("/agents/", tags=["AI Agent"])
def get_agent_list():
    """
    Returns a list of all available AI agent personas.
    """
    return {
        agent_name: {
            "name": data["name"],
            "description": data["description"]
        } for agent_name, data in AGENTS.items()
    }


@router.post("/agent-play/{agent_name}", response_model=schema.AgentPlayResponse, tags=["AI Agent"])
def agent_plays_a_turn(agent_name: str, db: Session = Depends(get_db)):
    """
    Triggers a specific AI agent to play a random turn.
    The agent picks a question, answers it based on its persona, and self-verifies.
    """
    if agent_name not in AGENTS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent '{agent_name}' not found. Available agents are: {list(AGENTS.keys())}"
        )

    selected_agent = AGENTS[agent_name]

    agent_result = agent.play_turn(
        db=db,
        agent_name=selected_agent["name"],
        system_prompt=selected_agent["system_prompt"],
        skill_level=selected_agent["skill_level"]
    )
    return agent_result