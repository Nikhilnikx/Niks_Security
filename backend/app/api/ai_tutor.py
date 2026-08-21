import httpx
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from app.database import get_db
from app.models.user import User
from app.models.concept import Concept
from app.models.topic import Topic
from app.models.domain import Domain
from app.models.ai_conversation import AIConversation, AIMessage
from app.config import get_settings
from app.auth import get_current_user

router = APIRouter(prefix="/api/ai", tags=["ai-tutor"])
settings = get_settings()


class ChatRequest(BaseModel):
    message: str
    certification_id: Optional[int] = None
    concept_id: Optional[int] = None
    conversation_id: Optional[int] = None


class GenerateFlashcardsRequest(BaseModel):
    concept_id: int
    count: int = 5


# --- AI Provider Abstraction ---

async def ollama_generate(prompt: str, system_prompt: str = "") -> str:
    """Call Ollama API for text generation."""
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{settings.OLLAMA_BASE_URL}/api/generate",
                json={
                    "model": settings.OLLAMA_MODEL,
                    "prompt": prompt,
                    "system": system_prompt,
                    "stream": False,
                },
            )
            if response.status_code == 200:
                data = response.json()
                return data.get("response", "")
            else:
                return "AI service is temporarily unavailable. Please try again later."
    except Exception as e:
        return "AI Tutor is currently unavailable. You can still use: Learning, Practice, Mock Exams, Flashcards, and Progress Tracking."


async def ollama_chat(messages: list, system_prompt: str = "") -> str:
    """Call Ollama API for chat."""
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{settings.OLLAMA_BASE_URL}/api/chat",
                json={
                    "model": settings.OLLAMA_MODEL,
                    "messages": [{"role": "system", "content": system_prompt}] + messages,
                    "stream": False,
                },
            )
            if response.status_code == 200:
                data = response.json()
                return data.get("message", {}).get("content", "")
            else:
                return "AI service is temporarily unavailable."
    except Exception:
        return "AI Tutor is currently unavailable. You can still use: Learning, Practice, Mock Exams, Flashcards, and Progress Tracking."


# --- Chat with AI Tutor ---

@router.post("/chat")
async def chat_with_ai(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Get or create conversation
    if request.conversation_id:
        conversation = db.query(AIConversation).filter(
            AIConversation.id == request.conversation_id,
            AIConversation.user_id == current_user.id,
        ).first()
    else:
        conversation = AIConversation(
            user_id=current_user.id,
            certification_id=request.certification_id,
            title=request.message[:100],
        )
        db.add(conversation)
        db.flush()

    # Build context from knowledge base
    context_parts = []

    # If specific concept is referenced
    if request.concept_id:
        concept = db.query(Concept).filter(Concept.id == request.concept_id).first()
        if concept:
            context_parts.append(f"Concept: {concept.name}")
            if concept.short_definition:
                context_parts.append(f"Definition: {concept.short_definition}")
            if concept.detailed_explanation:
                context_parts.append(f"Explanation: {concept.detailed_explanation}")
            if concept.key_points:
                context_parts.append(f"Key Points: {concept.key_points}")
            if concept.exam_tips:
                context_parts.append(f"Exam Tips: {concept.exam_tips}")

    # Search for relevant concepts based on the question
    search_terms = request.message.lower().split()
    for term in search_terms:
        if len(term) > 3:
            concepts = db.query(Concept).filter(
                Concept.name.ilike(f"%{term}%")
            ).limit(3).all()
            for c in concepts:
                if c.short_definition and c.id != request.concept_id:
                    context_parts.append(f"Related: {c.name} - {c.short_definition}")

    context = "\n".join(context_parts) if context_parts else "No specific context found in knowledge base."

    # Build system prompt
    system_prompt = f"""You are Niksmind AI Tutor, a helpful certification preparation assistant.

IMPORTANT RULES:
- Only provide information based on the knowledge base provided
- If the knowledge base doesn't have enough information, say: "Niksmind does not currently have enough verified information to answer this confidently."
- Do NOT invent or guess certification exam content
- Focus on explaining concepts clearly for learning
- Provide exam tips when relevant
- Be encouraging and supportive

Knowledge Base Context:
{context}

User question: {request.message}"""

    # Get conversation history
    history = db.query(AIMessage).filter(
        AIMessage.conversation_id == conversation.id
    ).order_by(AIMessage.created_at).all()

    messages = [{"role": msg.role, "content": msg.content} for msg in history]
    messages.append({"role": "user", "content": request.message})

    # Get AI response
    ai_response = await ollama_chat(messages, system_prompt)

    # Save messages
    user_msg = AIMessage(
        conversation_id=conversation.id,
        role="user",
        content=request.message,
    )
    assistant_msg = AIMessage(
        conversation_id=conversation.id,
        role="assistant",
        content=ai_response,
    )
    db.add(user_msg)
    db.add(assistant_msg)
    db.commit()

    return {
        "conversation_id": conversation.id,
        "response": ai_response,
        "context_used": bool(context_parts),
    }


# --- Get Conversations ---

@router.get("/conversations")
async def get_conversations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    conversations = db.query(AIConversation).filter(
        AIConversation.user_id == current_user.id,
    ).order_by(AIConversation.updated_at.desc()).limit(20).all()

    return {
        "conversations": [
            {
                "id": c.id,
                "title": c.title,
                "created_at": c.created_at.isoformat(),
                "updated_at": c.updated_at.isoformat(),
            }
            for c in conversations
        ]
    }


# --- Generate Flashcards with AI ---

@router.post("/generate-flashcards")
async def generate_flashcards(
    request: GenerateFlashcardsRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    concept = db.query(Concept).filter(Concept.id == request.concept_id).first()
    if not concept:
        raise HTTPException(status_code=404, detail="Concept not found")

    prompt = f"""Generate {request.count} flashcards for the following certification concept:

Concept: {concept.name}
Definition: {concept.short_definition or 'N/A'}
Key Points: {concept.key_points or 'N/A'}
Exam Tips: {concept.exam_tips or 'N/A'}

Format each flashcard as:
Q: [question]
A: [answer]

Generate exactly {request.count} flashcards focused on exam preparation."""

    system_prompt = "You are a certification study assistant. Generate clear, concise flashcards for exam preparation. Focus on key concepts and exam-relevant information."

    response = await ollama_generate(prompt, system_prompt)

    # Parse flashcards from response
    flashcards = []
    lines = response.strip().split("\n")
    current_front = None
    current_back = None

    for line in lines:
        line = line.strip()
        if line.startswith("Q:") or line.startswith("Q :"):
            if current_front and current_back:
                flashcards.append({"front": current_front, "back": current_back})
            current_front = line[2:].strip()
            current_back = None
        elif line.startswith("A:") or line.startswith("A :"):
            current_back = line[2:].strip()

    if current_front and current_back:
        flashcards.append({"front": current_front, "back": current_back})

    return {
        "concept_id": concept.id,
        "concept_name": concept.name,
        "flashcards": flashcards[:request.count],
    }


# --- Generate Summary with AI ---

@router.post("/summarize")
async def summarize_topic(
    topic_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")

    concepts = db.query(Concept).filter(Concept.topic_id == topic_id).all()
    concepts_text = "\n".join([
        f"- {c.name}: {c.short_definition or 'N/A'}"
        for c in concepts
    ])

    prompt = f"""Summarize the following certification topic for exam preparation:

Topic: {topic.name}
Domain: {topic.domain.name if topic.domain else 'N/A'}

Concepts:
{concepts_text}

Provide a clear, concise summary covering:
1. What this topic covers
2. Key concepts to remember
3. Common exam patterns
4. Study recommendations"""

    system_prompt = "You are a certification study assistant. Provide clear, exam-focused summaries."

    summary = await ollama_generate(prompt, system_prompt)

    return {
        "topic_id": topic.id,
        "topic_name": topic.name,
        "summary": summary,
    }
