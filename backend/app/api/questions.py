from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from app.database import get_db
from app.models.question import Question, QuestionOption, AccessLevel, QuestionDifficulty
from app.models.user import User
from app.models.user_answer import UserAnswer
from app.models.quiz import Quiz, QuizQuestion, QuizStatus
from app.models.product import UserEntitlement, EntitlementStatus
from app.auth import get_current_user

router = APIRouter(prefix="/api", tags=["questions"])


# --- Request/Response Models ---

class StartQuizRequest(BaseModel):
    certification_id: int
    quiz_type: str  # quick, topic, domain, weak_areas, random
    topic_id: Optional[int] = None
    domain_id: Optional[int] = None
    num_questions: int = 10
    difficulty: Optional[str] = None


class AnswerQuestionRequest(BaseModel):
    question_id: int
    selected_option_id: int


class QuizResponse(BaseModel):
    id: int
    quiz_type: str
    total_questions: int
    correct_answers: int
    score: int
    status: str
    questions: List[dict] = []


class QuestionBrief(BaseModel):
    id: int
    question_text: str
    question_type: str
    difficulty: Optional[str]
    options: List[dict]

    class Config:
        from_attributes = True


# --- Helper: check premium entitlement ---

def check_premium_access(user_id: int, certification_id: int, db: Session) -> bool:
    entitlement = db.query(UserEntitlement).join(
        # We'll check via product -> certification
    ).filter(
        UserEntitlement.user_id == user_id,
        UserEntitlement.status == EntitlementStatus.ACTIVE,
    ).first()
    if entitlement:
        return True

    # Also check direct certification product
    from app.models.product import Product
    product = db.query(Product).filter(
        Product.certification_id == certification_id,
        Product.active == True,
    ).first()
    if product:
        ent = db.query(UserEntitlement).filter(
            UserEntitlement.user_id == user_id,
            UserEntitlement.product_id == product.id,
            UserEntitlement.status == EntitlementStatus.ACTIVE,
        ).first()
        return ent is not None
    return False


# --- Helper: select questions based on algorithm ---

def select_questions(
    db: Session,
    exam_version_id: int,
    domain_id: Optional[int],
    topic_id: Optional[int],
    num_questions: int,
    access_level: AccessLevel,
    user_id: Optional[int] = None,
    difficulty: Optional[str] = None,
) -> List[Question]:
    query = db.query(Question).filter(
        Question.exam_version_id == exam_version_id,
        Question.access_level == access_level,
    )

    if domain_id:
        query = query.filter(Question.domain_id == domain_id)
    if topic_id:
        query = query.filter(Question.topic_id == topic_id)
    if difficulty:
        query = query.filter(Question.difficulty == difficulty)

    # Get previously answered question IDs for this user
    answered_ids = set()
    if user_id:
        answered = db.query(UserAnswer.question_id).filter(
            UserAnswer.user_id == user_id
        ).distinct().all()
        answered_ids = {a[0] for a in answered}

    all_questions = query.all()

    # Score questions: prioritize unanswered, weaker topics, harder difficulty
    scored = []
    for q in all_questions:
        score = 0
        if q.id not in answered_ids:
            score += 10  # Prioritize unseen questions
        if q.difficulty == QuestionDifficulty.HARD:
            score += 3
        elif q.difficulty == QuestionDifficulty.MEDIUM:
            score += 2
        else:
            score += 1
        scored.append((score, q))

    # Sort by score descending, take top N
    scored.sort(key=lambda x: x[0], reverse=True)
    selected = [q for _, q in scored[:num_questions]]

    # If not enough, fill with remaining
    if len(selected) < num_questions:
        remaining = [q for _, q in scored if q not in selected]
        selected.extend(remaining[:num_questions - len(selected)])

    return selected


# --- Question List (Admin/Content) ---

@router.get("/questions")
async def list_questions(
    exam_version_id: Optional[int] = None,
    domain_id: Optional[int] = None,
    topic_id: Optional[int] = None,
    access_level: Optional[str] = None,
    difficulty: Optional[str] = None,
    page: int = 1,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(Question)
    if exam_version_id:
        query = query.filter(Question.exam_version_id == exam_version_id)
    if domain_id:
        query = query.filter(Question.domain_id == domain_id)
    if topic_id:
        query = query.filter(Question.topic_id == topic_id)
    if access_level:
        query = query.filter(Question.access_level == access_level)
    if difficulty:
        query = query.filter(Question.difficulty == difficulty)

    total = query.count()
    questions = query.offset((page - 1) * limit).limit(limit).all()

    return {
        "total": total,
        "page": page,
        "limit": limit,
        "questions": [
            {
                "id": q.id,
                "question_text": q.question_text,
                "question_type": q.question_type.value,
                "difficulty": q.difficulty.value if q.difficulty else None,
                "access_level": q.access_level.value,
                "explanation": q.explanation,
                "options": [
                    {"id": o.id, "text": o.option_text, "is_correct": o.is_correct}
                    for o in q.options
                ],
            }
            for q in questions
        ],
    }


# --- Start Quiz ---

@router.post("/quizzes/start")
async def start_quiz(
    request: StartQuizRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Find active exam version
    from app.models.certification import ExamVersion
    exam_version = db.query(ExamVersion).filter(
        ExamVersion.certification_id == request.certification_id,
        ExamVersion.status == "active",
    ).first()
    if not exam_version:
        exam_version = db.query(ExamVersion).filter(
            ExamVersion.certification_id == request.certification_id,
        ).order_by(ExamVersion.effective_date.desc()).first()
    if not exam_version:
        raise HTTPException(status_code=404, detail="No exam version found")

    # Check if user has premium access
    has_premium = check_premium_access(current_user.id, request.certification_id, db)
    access_level = AccessLevel.FREE

    # Select questions
    questions = select_questions(
        db=db,
        exam_version_id=exam_version.id,
        domain_id=request.domain_id,
        topic_id=request.topic_id,
        num_questions=request.num_questions,
        access_level=access_level,
        user_id=current_user.id,
        difficulty=request.difficulty,
    )

    if not questions:
        raise HTTPException(status_code=404, detail="No questions available for this selection")

    # Create quiz
    quiz = Quiz(
        user_id=current_user.id,
        certification_id=request.certification_id,
        quiz_type=request.quiz_type,
        domain_id=request.domain_id,
        topic_id=request.topic_id,
        total_questions=len(questions),
    )
    db.add(quiz)
    db.flush()

    # Add questions to quiz
    for i, q in enumerate(questions):
        qq = QuizQuestion(
            quiz_id=quiz.id,
            question_id=q.id,
            order_index=i + 1,
        )
        db.add(qq)

    db.commit()
    db.refresh(quiz)

    return {
        "id": quiz.id,
        "quiz_type": quiz.quiz_type,
        "total_questions": quiz.total_questions,
        "certification_id": quiz.certification_id,
        "questions": [
            {
                "id": q.id,
                "question_text": q.question_text,
                "question_type": q.question_type.value,
                "difficulty": q.difficulty.value if q.difficulty else None,
                "options": [
                    {"id": o.id, "text": o.option_text}
                    for o in q.options
                ],
            }
            for q in questions
        ],
    }


# --- Answer Question ---

@router.post("/quizzes/{quiz_id}/answer")
async def answer_quiz_question(
    quiz_id: int,
    request: AnswerQuestionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    quiz = db.query(Quiz).filter(
        Quiz.id == quiz_id,
        Quiz.user_id == current_user.id,
    ).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    if quiz.status == QuizStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Quiz already completed")

    qq = db.query(QuizQuestion).filter(
        QuizQuestion.quiz_id == quiz_id,
        QuizQuestion.question_id == request.question_id,
    ).first()
    if not qq:
        raise HTTPException(status_code=404, detail="Question not in this quiz")

    # Check if already answered
    if qq.is_correct is not None:
        raise HTTPException(status_code=400, detail="Question already answered")

    # Verify correct answer
    correct_option = db.query(QuestionOption).filter(
        QuestionOption.question_id == request.question_id,
        QuestionOption.is_correct == True,
    ).first()

    is_correct = correct_option and correct_option.id == request.selected_option_id

    # Update quiz question
    qq.selected_option_id = request.selected_option_id
    qq.is_correct = 1 if is_correct else 0

    # Update quiz score
    if is_correct:
        quiz.correct_answers += 1

    # Record user answer
    user_answer = UserAnswer(
        user_id=current_user.id,
        question_id=request.question_id,
        selected_option_id=request.selected_option_id,
        is_correct=is_correct,
    )
    db.add(user_answer)

    db.commit()

    return {
        "is_correct": is_correct,
        "correct_option_id": correct_option.id if correct_option else None,
        "explanation": db.query(Question).filter(Question.id == request.question_id).first().explanation,
    }


# --- Complete Quiz ---

@router.post("/quizzes/{quiz_id}/complete")
async def complete_quiz(
    quiz_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    quiz = db.query(Quiz).filter(
        Quiz.id == quiz_id,
        Quiz.user_id == current_user.id,
    ).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    quiz.status = QuizStatus.COMPLETED
    quiz.completed_at = datetime.utcnow()
    quiz.score = int((quiz.correct_answers / quiz.total_questions) * 100) if quiz.total_questions > 0 else 0

    # Update mastery scores
    from app.models.user_progress import UserProgress
    progress = db.query(UserProgress).filter(
        UserProgress.user_id == current_user.id,
        UserProgress.certification_id == quiz.certification_id,
    ).first()
    if progress:
        progress.total_questions_attempted += quiz.total_questions
        progress.correct_answers += quiz.correct_answers
    else:
        progress = UserProgress(
            user_id=current_user.id,
            certification_id=quiz.certification_id,
            total_questions_attempted=quiz.total_questions,
            correct_answers=quiz.correct_answers,
        )
        db.add(progress)

    db.commit()
    db.refresh(quiz)

    # Get all quiz questions with details
    quiz_questions = db.query(QuizQuestion).filter(
        QuizQuestion.quiz_id == quiz_id
    ).order_by(QuizQuestion.order_index).all()

    questions_detail = []
    for qq in quiz_questions:
        q = db.query(Question).filter(Question.id == qq.question_id).first()
        correct_opt = db.query(QuestionOption).filter(
            QuestionOption.question_id == qq.question_id,
            QuestionOption.is_correct == True,
        ).first()
        questions_detail.append({
            "question_text": q.question_text if q else None,
            "selected_option_id": qq.selected_option_id,
            "correct_option_id": correct_opt.id if correct_opt else None,
            "is_correct": qq.is_correct == 1 if qq.is_correct is not None else None,
            "explanation": q.explanation if q else None,
        })

    return {
        "id": quiz.id,
        "score": quiz.score,
        "correct_answers": quiz.correct_answers,
        "total_questions": quiz.total_questions,
        "status": quiz.status.value,
        "questions": questions_detail,
    }
