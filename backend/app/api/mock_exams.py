from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from app.database import get_db
from app.models.mock_exam import MockExam, MockExamQuestion, MockExamConfig, MockExamStatus
from app.models.question import Question, QuestionOption, AccessLevel
from app.models.domain import Domain
from app.models.user import User
from app.auth import get_current_user
from app.api.questions import check_premium_access

router = APIRouter(prefix="/api/mock-exams", tags=["mock-exams"])


class StartMockExamRequest(BaseModel):
    certification_id: int


class AnswerMockExamRequest(BaseModel):
    question_id: int
    selected_option_id: int


class FlagQuestionRequest(BaseModel):
    question_id: int
    flagged: bool


# --- Start Mock Exam ---

@router.post("/start")
async def start_mock_exam(
    request: StartMockExamRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Check premium access
    has_premium = check_premium_access(current_user.id, request.certification_id, db)

    # Get exam config
    config = db.query(MockExamConfig).filter(
        MockExamConfig.certification_id == request.certification_id,
    ).first()

    if not config:
        # Default config
        from app.models.certification import ExamVersion
        exam_version = db.query(ExamVersion).filter(
            ExamVersion.certification_id == request.certification_id,
        ).first()
        if not exam_version:
            raise HTTPException(status_code=404, detail="No exam version found")

        # Create default config
        config = MockExamConfig(
            certification_id=request.certification_id,
            number_of_questions=50,
            duration_minutes=90,
            passing_score=70,
        )
        db.add(config)
        db.flush()

    # Get domains and their weights
    exam_version = db.query(Domain).filter(
        Domain.exam_version_id == db.query(
            func.min(Domain.exam_version_id)
        ).scalar()
    ).all() if False else None

    # Get active exam version domains
    from app.models.certification import ExamVersion
    ev = db.query(ExamVersion).filter(
        ExamVersion.certification_id == request.certification_id,
        ExamVersion.status == "active",
    ).first()
    if not ev:
        ev = db.query(ExamVersion).filter(
            ExamVersion.certification_id == request.certification_id,
        ).first()
    if not ev:
        raise HTTPException(status_code=404, detail="No exam version found")

    domains = db.query(Domain).filter(Domain.exam_version_id == ev.id).all()
    if not domains:
        raise HTTPException(status_code=404, detail="No domains found")

    # Distribute questions by domain weight
    total_questions = config.number_of_questions
    selected_questions = []
    used_ids = set()

    for domain in domains:
        num_for_domain = max(1, int(total_questions * domain.weight_percentage / 100))
        questions = db.query(Question).filter(
            Question.exam_version_id == ev.id,
            Question.domain_id == domain.id,
            Question.id.notin_(used_ids),
        ).order_by(func.random()).limit(num_for_domain).all()

        for q in questions:
            if q.id not in used_ids:
                selected_questions.append(q)
                used_ids.add(q.id)

    # Fill remaining if needed
    if len(selected_questions) < total_questions:
        remaining = db.query(Question).filter(
            Question.exam_version_id == ev.id,
            Question.id.notin_(used_ids),
        ).order_by(func.random()).limit(total_questions - len(selected_questions)).all()
        selected_questions.extend(remaining)

    selected_questions = selected_questions[:total_questions]

    # Create mock exam
    mock_exam = MockExam(
        user_id=current_user.id,
        certification_id=request.certification_id,
        total_questions=len(selected_questions),
        duration_minutes=config.duration_minutes,
    )
    db.add(mock_exam)
    db.flush()

    # Add questions
    for i, q in enumerate(selected_questions):
        mq = MockExamQuestion(
            mock_exam_id=mock_exam.id,
            question_id=q.id,
            order_index=i + 1,
        )
        db.add(mq)

    db.commit()
    db.refresh(mock_exam)

    return {
        "id": mock_exam.id,
        "total_questions": mock_exam.total_questions,
        "duration_minutes": mock_exam.duration_minutes,
        "started_at": mock_exam.started_at.isoformat(),
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
            for q in selected_questions
        ],
    }


# --- Answer Mock Exam Question ---

@router.post("/{exam_id}/answer")
async def answer_mock_exam_question(
    exam_id: int,
    request: AnswerMockExamRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    mock_exam = db.query(MockExam).filter(
        MockExam.id == exam_id,
        MockExam.user_id == current_user.id,
    ).first()
    if not mock_exam:
        raise HTTPException(status_code=404, detail="Mock exam not found")
    if mock_exam.status == MockExamStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Mock exam already completed")

    mq = db.query(MockExamQuestion).filter(
        MockExamQuestion.mock_exam_id == exam_id,
        MockExamQuestion.question_id == request.question_id,
    ).first()
    if not mq:
        raise HTTPException(status_code=404, detail="Question not in this mock exam")

    if mq.is_correct is not None:
        raise HTTPException(status_code=400, detail="Question already answered")

    correct_option = db.query(QuestionOption).filter(
        QuestionOption.question_id == request.question_id,
        QuestionOption.is_correct == True,
    ).first()

    is_correct = correct_option and correct_option.id == request.selected_option_id

    mq.selected_option_id = request.selected_option_id
    mq.is_correct = 1 if is_correct else 0

    if is_correct:
        mock_exam.correct_answers += 1

    db.commit()

    return {"is_correct": is_correct}


# --- Flag Question ---

@router.post("/{exam_id}/flag")
async def flag_question(
    exam_id: int,
    request: FlagQuestionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    mq = db.query(MockExamQuestion).filter(
        MockExamQuestion.mock_exam_id == exam_id,
        MockExamQuestion.question_id == request.question_id,
    ).first()
    if not mq:
        raise HTTPException(status_code=404, detail="Question not found")

    mq.flagged = 1 if request.flagged else 0
    db.commit()

    return {"flagged": request.flagged}


# --- Submit Mock Exam ---

@router.post("/{exam_id}/submit")
async def submit_mock_exam(
    exam_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    mock_exam = db.query(MockExam).filter(
        MockExam.id == exam_id,
        MockExam.user_id == current_user.id,
    ).first()
    if not mock_exam:
        raise HTTPException(status_code=404, detail="Mock exam not found")

    mock_exam.status = MockExamStatus.COMPLETED
    mock_exam.completed_at = datetime.utcnow()
    mock_exam.time_spent = int((mock_exam.completed_at - mock_exam.started_at).total_seconds())
    mock_exam.score = int((mock_exam.correct_answers / mock_exam.total_questions) * 100) if mock_exam.total_questions > 0 else 0

    # Get domain performance
    domain_scores = {}
    mock_questions = db.query(MockExamQuestion).filter(
        MockExamQuestion.mock_exam_id == exam_id
    ).all()

    for mq in mock_questions:
        q = db.query(Question).filter(Question.id == mq.question_id).first()
        if q:
            domain = db.query(Domain).filter(Domain.id == q.domain_id).first()
            if domain:
                if domain.name not in domain_scores:
                    domain_scores[domain.name] = {"correct": 0, "total": 0, "weight": domain.weight_percentage}
                domain_scores[domain.name]["total"] += 1
                if mq.is_correct == 1:
                    domain_scores[domain.name]["correct"] += 1

    domain_performance = {}
    for name, data in domain_scores.items():
        domain_performance[name] = {
            "correct": data["correct"],
            "total": data["total"],
            "percentage": int((data["correct"] / data["total"]) * 100) if data["total"] > 0 else 0,
            "weight": data["weight"],
        }

    # Identify weak areas
    weak_areas = [
        name for name, data in domain_performance.items()
        if data["percentage"] < 70
    ]
    strong_areas = [
        name for name, data in domain_performance.items()
        if data["percentage"] >= 70
    ]

    db.commit()
    db.refresh(mock_exam)

    return {
        "id": mock_exam.id,
        "score": mock_exam.score,
        "correct_answers": mock_exam.correct_answers,
        "total_questions": mock_exam.total_questions,
        "time_spent": mock_exam.time_spent,
        "duration_minutes": mock_exam.duration_minutes,
        "status": mock_exam.status.value,
        "domain_performance": domain_performance,
        "weak_areas": weak_areas,
        "strong_areas": strong_areas,
    }


# --- Get Mock Exam Results ---

@router.get("/{exam_id}")
async def get_mock_exam(
    exam_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    mock_exam = db.query(MockExam).filter(
        MockExam.id == exam_id,
        MockExam.user_id == current_user.id,
    ).first()
    if not mock_exam:
        raise HTTPException(status_code=404, detail="Mock exam not found")

    questions = db.query(MockExamQuestion).filter(
        MockExamQuestion.mock_exam_id == exam_id
    ).order_by(MockExamQuestion.order_index).all()

    questions_detail = []
    for mq in questions:
        q = db.query(Question).filter(Question.id == mq.question_id).first()
        correct_opt = db.query(QuestionOption).filter(
            QuestionOption.question_id == mq.question_id,
            QuestionOption.is_correct == True,
        ).first()
        questions_detail.append({
            "id": q.id if q else None,
            "question_text": q.question_text if q else None,
            "selected_option_id": mq.selected_option_id,
            "correct_option_id": correct_opt.id if correct_opt else None,
            "is_correct": mq.is_correct == 1 if mq.is_correct is not None else None,
            "flagged": mq.flagged == 1,
            "order_index": mq.order_index,
        })

    return {
        "id": mock_exam.id,
        "score": mock_exam.score,
        "correct_answers": mock_exam.correct_answers,
        "total_questions": mock_exam.total_questions,
        "time_spent": mock_exam.time_spent,
        "duration_minutes": mock_exam.duration_minutes,
        "status": mock_exam.status.value,
        "questions": questions_detail,
    }
