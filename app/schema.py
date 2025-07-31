from pydantic import BaseModel


class Question(BaseModel):
    question_id: int
    round: str
    category: str
    value: str
    question: str

    class Config:
        from_attributes = True


class VerifyAnswerRequest(BaseModel):
    question_id: int
    user_answer: str


class VerifyAnswerResponse(BaseModel):
    is_correct: bool
    ai_response: str

class AgentPlayResponse(BaseModel):
    agent_name: str
    question: str
    ai_answer: str
    ai_explanation: str | None = None
    is_correct: bool
