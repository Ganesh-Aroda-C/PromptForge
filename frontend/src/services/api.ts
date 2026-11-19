import {
  Project,
  TaskUnderstanding,
  PromptRefinement,
  EvolutionaryOptimizationResult,
  GeneratedImage,
  ImageEvaluation,
  Dataset,
  DatasetRecord,
  SystemStatus
} from '../types';

const API_BASE = '/api';

export const api = {
  // System Health & Status
  async getSystemStatus(): Promise<SystemStatus> {
    const res = await fetch(`${API_BASE}/settings/status`);
    if (!res.ok) throw new Error('Failed to fetch system status');
    return res.json();
  },

  async updateSettings(payload: Record<string, any>): Promise<any> {
    const res = await fetch(`${API_BASE}/settings/update`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (!res.ok) throw new Error('Failed to update settings');
    return res.json();
  },

  // Projects
  async listProjects(category?: string): Promise<Project[]> {
    const url = category ? `${API_BASE}/projects?category=${encodeURIComponent(category)}` : `${API_BASE}/projects`;
    const res = await fetch(url);
    if (!res.ok) throw new Error('Failed to fetch projects');
    return res.json();
  },

  async getProject(projectId: string): Promise<Project> {
    const res = await fetch(`${API_BASE}/projects/${projectId}`);
    if (!res.ok) throw new Error('Failed to fetch project');
    return res.json();
  },

  async createProject(data: { title: string; description?: string; category: string; tags: string[] }): Promise<Project> {
    const res = await fetch(`${API_BASE}/projects`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    if (!res.ok) throw new Error('Failed to create project');
    return res.json();
  },

  async deleteProject(projectId: string): Promise<void> {
    const res = await fetch(`${API_BASE}/projects/${projectId}`, {
      method: 'DELETE'
    });
    if (!res.ok) throw new Error('Failed to delete project');
  },

  // AI Pipeline & Prompts
  async enhancePrompt(prompt: string, visualStyle?: string, category?: string): Promise<any> {
    const res = await fetch(`${API_BASE}/prompts/enhance`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        prompt: prompt,
        visual_style: visualStyle,
        category: category
      })
    });
    if (!res.ok) throw new Error('Failed to enhance prompt');
    return res.json();
  },

  async understandTask(prompt: string, category?: string): Promise<TaskUnderstanding> {
    const res = await fetch(`${API_BASE}/prompts/understand`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt, category })
    });
    if (!res.ok) throw new Error('Failed to analyze task');
    return res.json();
  },

  async refinePrompt(originalPrompt: string, stylePreference?: string, category?: string): Promise<PromptRefinement> {
    const res = await fetch(`${API_BASE}/prompts/refine`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        original_prompt: originalPrompt,
        style_preference: stylePreference,
        category: category
      })
    });
    if (!res.ok) throw new Error('Failed to refine prompt');
    return res.json();
  },

  async optimizePrompt(params: {
    initial_prompt: string;
    task_type?: string;
    population_size?: number;
    num_generations?: number;
    mutation_rate?: number;
    seed?: number;
  }): Promise<EvolutionaryOptimizationResult> {
    const res = await fetch(`${API_BASE}/prompts/optimize`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        initial_prompt: params.initial_prompt,
        task_type: params.task_type || 'industrial_design',
        population_size: params.population_size || 6,
        num_generations: params.num_generations || 4,
        mutation_rate: params.mutation_rate || 0.4,
        seed: params.seed || 42
      })
    });
    if (!res.ok) throw new Error('Failed to optimize prompt with evolutionary search');
    return res.json();
  },

  // Image Generation
  async generateImages(params: {
    prompt: string;
    negative_prompt?: string;
    project_id?: string;
    num_images?: number;
    aspect_ratio?: string;
    width?: number;
    height?: number;
    seed?: number;
    conditioning?: {
      enabled: boolean;
      conditioning_type: string;
      image_data?: string;
      strength: number;
    };
  }): Promise<{ success: boolean; generations: GeneratedImage[]; message: string; mode: string }> {
    const res = await fetch(`${API_BASE}/generation/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params)
    });
    if (!res.ok) throw new Error('Failed to generate images');
    return res.json();
  },

  async listGenerations(projectId?: string, limit: number = 50): Promise<GeneratedImage[]> {
    const url = projectId ? `${API_BASE}/generation/history?project_id=${projectId}&limit=${limit}` : `${API_BASE}/generation/history?limit=${limit}`;
    const res = await fetch(url);
    if (!res.ok) throw new Error('Failed to fetch generation history');
    return res.json();
  },

  async processConditioning(conditioningType: string, imageData: string): Promise<any> {
    const res = await fetch(`${API_BASE}/generation/condition`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        conditioning_type: conditioningType,
        image_data: imageData
      })
    });
    if (!res.ok) throw new Error('Failed to process structural conditioning');
    return res.json();
  },

  // Image Evaluation (VQA + CLIP)
  async evaluateImage(params: {
    generation_id: string;
    image_url: string;
    prompt: string;
    expected_objects?: string[];
  }): Promise<ImageEvaluation> {
    const res = await fetch(`${API_BASE}/evaluation/evaluate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params)
    });
    if (!res.ok) throw new Error('Failed to evaluate image');
    return res.json();
  },

  async listEvaluations(generationId?: string): Promise<ImageEvaluation[]> {
    const url = generationId ? `${API_BASE}/evaluation/history?generation_id=${generationId}` : `${API_BASE}/evaluation/history`;
    const res = await fetch(url);
    if (!res.ok) throw new Error('Failed to fetch evaluation history');
    return res.json();
  },

  async refineClosedLoop(currentPrompt: string, evaluation: ImageEvaluation, iteration: number): Promise<any> {
    const res = await fetch(`${API_BASE}/evaluation/refine-loop`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        current_prompt: currentPrompt,
        evaluation: evaluation,
        iteration: iteration,
        max_iterations: 3
      })
    });
    if (!res.ok) throw new Error('Failed to execute closed-loop refinement step');
    return res.json();
  },

  // Dataset Studio
  async listDatasets(): Promise<Dataset[]> {
    const res = await fetch(`${API_BASE}/datasets`);
    if (!res.ok) throw new Error('Failed to fetch datasets');
    return res.json();
  },

  async getDataset(datasetId: string): Promise<Dataset> {
    const res = await fetch(`${API_BASE}/datasets/${datasetId}`);
    if (!res.ok) throw new Error('Failed to fetch dataset');
    return res.json();
  },

  async createDataset(data: { name: string; description: string; source: string; task_category: string; records: DatasetRecord[] }): Promise<Dataset> {
    const res = await fetch(`${API_BASE}/datasets/create`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    if (!res.ok) throw new Error('Failed to create dataset');
    return res.json();
  },

  async addDatasetRecord(datasetId: string, record: DatasetRecord): Promise<any> {
    const res = await fetch(`${API_BASE}/datasets/${datasetId}/records`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(record)
    });
    if (!res.ok) throw new Error('Failed to add record');
    return res.json();
  },

  async deleteDatasetRecord(datasetId: string, recordId: string): Promise<any> {
    const res = await fetch(`${API_BASE}/datasets/${datasetId}/records/${recordId}`, {
      method: 'DELETE'
    });
    if (!res.ok) throw new Error('Failed to delete record');
    return res.json();
  },

  async deleteDataset(datasetId: string): Promise<any> {
    const res = await fetch(`${API_BASE}/datasets/${datasetId}`, {
      method: 'DELETE'
    });
    if (!res.ok) throw new Error('Failed to delete dataset');
    return res.json();
  }
};
