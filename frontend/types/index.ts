export interface Provider {
  id: number;
  name: string;
  slug: string;
  description?: string;
  logo?: string;
  website_url?: string;
}

export interface Certification {
  id: number;
  name: string;
  slug: string;
  code: string;
  description?: string;
  level: string;
  category: string;
  estimated_hours?: number;
  provider?: Provider;
}

export interface Domain {
  id: number;
  name: string;
  description?: string;
  weight_percentage: number;
  topics?: Topic[];
}

export interface Topic {
  id: number;
  name: string;
  slug: string;
  description?: string;
  domain?: Domain;
  concepts?: Concept[];
}

export interface Concept {
  id: number;
  name: string;
  slug: string;
  short_definition?: string;
  simple_explanation?: string;
  detailed_explanation?: string;
  examples?: string;
  key_points?: string;
  exam_tips?: string;
  common_mistakes?: string;
  difficulty?: string;
  topic?: Topic;
  learning_resources?: LearningResource[];
  related_concepts?: RelatedConcept[];
}

export interface RelatedConcept {
  id: number;
  name: string;
  slug: string;
  relationship: string;
}

export interface LearningResource {
  id: number;
  title: string;
  description?: string;
  url?: string;
  source?: string;
  resource_type: string;
  is_official: boolean;
}

export interface Question {
  id: number;
  question_text: string;
  question_type: string;
  difficulty?: string;
  access_level?: string;
  options: QuestionOption[];
  explanation?: string;
}

export interface QuestionOption {
  id: number;
  text: string;
  is_correct?: boolean;
}

export interface Quiz {
  id: number;
  quiz_type: string;
  total_questions: number;
  correct_answers: number;
  score: number;
  status: string;
  questions: Question[];
}

export interface MockExam {
  id: number;
  total_questions: number;
  duration_minutes: number;
  started_at: string;
  questions: Question[];
}

export interface ReadinessScore {
  knowledge_mastery: number;
  practice_accuracy: number;
  mock_performance: number;
  retention: number;
  overall_readiness: number;
  status: string;
  disclaimer: string;
}

export interface Dashboard {
  total_questions_attempted: number;
  total_correct: number;
  accuracy: number;
  certifications_count: number;
  recent_quizzes: QuizSummary[];
  recent_mock_exams: QuizSummary[];
}

export interface QuizSummary {
  id: number;
  quiz_type?: string;
  score: number;
  total_questions: number;
  correct_answers: number;
  completed_at?: string;
}

export interface Flashcard {
  id: number;
  front: string;
  back: string;
  type: string;
  confidence?: number;
  review_count?: number;
  next_review?: string;
}

export interface Product {
  id: number;
  name: string;
  slug: string;
  description?: string;
  price: number;
  currency: string;
  product_type: string;
  certification_id?: number;
}

export interface Document {
  id: number;
  filename: string;
  file_type: string;
  file_size: number;
  status: string;
  created_at: string;
}
