export interface Project {
  project_id: string;
  user_id?: string;
  title: string;
  description: string;
  category: string;
  tags: string[];
  generations_count: number;
  prompts_count: number;
  thumbnail_url?: string | null;
  created_at: string;
  updated_at?: string | null;
}

export interface SpatialConstraint {
  object_name: string;
  position: string;
  bbox?: number[];
}

export interface TaskUnderstanding {
  task_type: string;
  product_category: string;
  primary_subject: string;
  objects: string[];
  materials: string[];
  colors: string[];
  style: string;
  lighting: string;
  composition: string;
  spatial_constraints: SpatialConstraint[];
  ambiguous_terms: { term: string; intended_gloss: string; disambiguation_note?: string }[];
  missing_information: string[];
}

export interface PromptAlternative {
  title: string;
  positive_prompt: string;
  description: string;
}

export interface PromptRefinement {
  original_prompt: string;
  high_level_prompt: string;
  low_level_prompt: string;
  full_positive_prompt: string;
  negative_prompt: string;
  detected_objects: string[];
  materials: string[];
  style_preset: string;
  alternatives: PromptAlternative[];
  disambiguations: { term: string; intended_gloss: string }[];
}

export interface CandidatePrompt {
  candidate_id: string;
  prompt: string;
  fitness_score: number;
  metrics: Record<string, number>;
  generation: number;
  parent_ids: string[];
  mutation_type?: string | null;
}

export interface GenerationLog {
  generation_index: number;
  best_fitness: number;
  average_fitness: number;
  best_prompt: string;
  candidates: CandidatePrompt[];
}

export interface EvolutionaryOptimizationResult {
  initial_prompt: string;
  best_prompt: string;
  initial_fitness: number;
  best_fitness: number;
  improvement_percentage: number;
  total_generations: number;
  selected_metrics: string[];
  generation_history: GenerationLog[];
}

export interface GeneratedImage {
  generation_id: string;
  project_id?: string | null;
  image_url: string;
  thumbnail_url: string;
  prompt: string;
  negative_prompt: string;
  seed: number;
  width: number;
  height: number;
  model_name: string;
  provider: string;
  clip_score?: number | null;
  rank?: number | null;
  created_at: string;
}

export interface VQAProbe {
  question: string;
  expected_answer: string;
  observed_answer: string;
  is_aligned: boolean;
  category: string;
}

export interface ImageEvaluation {
  evaluation_id: string;
  generation_id: string;
  clip_similarity: number;
  prompt_adherence_score: number;
  overall_quality_score: number;
  detected_objects: string[];
  missing_requirements: string[];
  vqa_probes: VQAProbe[];
  discrepancy_summary: string;
  suggested_corrective_prompt: string;
  evaluation_status: string;
  created_at: string;
}

export interface DatasetRecord {
  record_id: string;
  task_type: string;
  product_category: string;
  input_prompt: string;
  optimized_prompt: string;
  negative_prompt: string;
  objects: string[];
  attributes: Record<string, any>;
  style: string;
  image_reference?: string | null;
  expected_constraints: string[];
  evaluation_metadata: Record<string, any>;
}

export interface Dataset {
  dataset_id: string;
  name: string;
  description: string;
  source: string;
  task_category: string;
  record_count: number;
  records?: DatasetRecord[];
  created_at: string;
  updated_at?: string | null;
}

export interface ServiceHealth {
  service_name: string;
  is_active: boolean;
  provider: string;
  details: string;
}

export interface SystemStatus {
  mode: 'live' | 'demo';
  database_connected: boolean;
  database_type: string;
  services: Record<string, ServiceHealth>;
  version: string;
}
