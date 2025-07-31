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
