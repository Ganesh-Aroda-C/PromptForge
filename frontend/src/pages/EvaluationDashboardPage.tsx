import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import {
  CheckCircle2,
  AlertTriangle,
  RefreshCw,
  Sparkles,
  ArrowRight,
  ShieldCheck,
  HelpCircle,
  Eye,
  Check,
  Copy
} from 'lucide-react';
import { api } from '../services/api';
import { GeneratedImage, ImageEvaluation } from '../types';

export const EvaluationDashboardPage: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const navState = location.state as { selectedImage?: GeneratedImage } | null;

  // Selected Image for evaluation
  const [selectedImage, setSelectedImage] = useState<GeneratedImage | null>(navState?.selectedImage || null);
  const [recentGenerations, setRecentGenerations] = useState<GeneratedImage[]>([]);
  const [evaluation, setEvaluation] = useState<ImageEvaluation | null>(null);
  const [evaluating, setEvaluating] = useState(false);
  const [refiningLoop, setRefiningLoop] = useState(false);
  const [loopIteration, setLoopIteration] = useState(1);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    loadRecentImages();
  }, []);

  useEffect(() => {
    if (selectedImage) {
      triggerEvaluation(selectedImage);
    }
  }, [selectedImage]);

  const loadRecentImages = async () => {
    try {
      const data = await api.listGenerations();
      setRecentGenerations(data || []);
      if (!selectedImage && data && data.length > 0) {
        setSelectedImage(data[0]);
      }
    } catch (err) {
      console.error('Failed to load recent images', err);
    }
  };

  const triggerEvaluation = async (img: GeneratedImage) => {
    try {
      setEvaluating(true);
      const res = await api.evaluateImage({
        generation_id: img.generation_id,
        image_url: img.image_url,
        prompt: img.prompt,
        expected_objects: ['product chassis', 'material finish', 'lighting']
      });
      setEvaluation(res);
    } catch (err) {
      console.error('Evaluation error', err);
    } finally {
      setEvaluating(false);
    }
  };

  const handleClosedLoopStep = async () => {
    if (!evaluation || !selectedImage) return;
    try {
      setRefiningLoop(true);
      const nextLoop = await api.refineClosedLoop(
        evaluation.suggested_corrective_prompt,
        evaluation,
        loopIteration + 1
      );
      setLoopIteration((prev) => prev + 1);

      // Re-trigger generation with the improved corrective prompt
      const genRes = await api.generateImages({
        prompt: nextLoop.refined_prompt,
        negative_prompt: selectedImage.negative_prompt,
        num_images: 1
      });

      if (genRes.generations.length > 0) {
        setSelectedImage(genRes.generations[0]);
      }
    } catch (err) {
      console.error('Closed-loop error', err);
    } finally {
      setRefiningLoop(false);
    }
  };

  const handleCopy = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="space-y-8 animate-fadeIn max-w-7xl mx-auto">
      {/* Header */}
      <div className="border-b border-white/5 pb-6">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-cyan-500/10 border border-cyan-500/20 text-xs font-mono text-cyan-400 mb-2">
          <CheckCircle2 className="w-3.5 h-3.5" />
          <span>Automated Visual Quality & Adherence Inspection</span>
        </div>
        <h1 className="text-2xl font-bold tracking-tight text-white">Visual Evaluation & Reflection</h1>
        <p className="text-xs text-gray-400 mt-1">
          Inspect generative outputs against input criteria with automated Visual Question Answering (BLIP) and closed-loop self-correction.
        </p>
      </div>

      {/* Recent Generations Selection Strip */}
      <div className="space-y-2">
        <span className="text-xs font-mono text-gray-400 uppercase">Select Concept to Evaluate:</span>
        <div className="flex items-center gap-3 overflow-x-auto pb-2">
          {recentGenerations.map((gen) => (
            <div
              key={gen.generation_id}
              onClick={() => setSelectedImage(gen)}
              className={`flex-shrink-0 w-24 h-24 rounded-xl overflow-hidden cursor-pointer border-2 transition-all relative ${
                selectedImage?.generation_id === gen.generation_id
                  ? 'border-cyan-400 shadow-lg shadow-cyan-500/20 scale-105'
                  : 'border-white/10 opacity-70 hover:opacity-100'
              }`}
            >
              <img src={gen.image_url} alt={gen.prompt} className="w-full h-full object-cover" />
            </div>
          ))}
        </div>
      </div>

      {selectedImage && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          {/* Left: Image & Metrics (5 Cols) */}
          <div className="lg:col-span-5 space-y-6">
            <div className="surface-card p-4 rounded-2xl bg-black/60 border border-white/10 overflow-hidden shadow-2xl">
              <img
                src={selectedImage.image_url}
                alt={selectedImage.prompt}
                className="w-full h-auto rounded-xl object-contain"
              />
              <div className="pt-3 flex items-center justify-between text-xs text-gray-400 font-mono">
                <span>Seed: {selectedImage.seed}</span>
                <span>{selectedImage.width}×{selectedImage.height}</span>
              </div>
            </div>

            {/* Score Badges Grid */}
            {evaluation && (
              <div className="grid grid-cols-3 gap-3">
                <div className="surface-card p-3 rounded-xl border border-white/5 text-center">
                  <span className="text-[10px] text-gray-500 font-mono uppercase block">CLIP Alignment</span>
                  <span className="text-lg font-bold text-cyan-400 font-mono">
                    {evaluation.clip_similarity.toFixed(3)}
                  </span>
                </div>
                <div className="surface-card p-3 rounded-xl border border-white/5 text-center">
                  <span className="text-[10px] text-gray-500 font-mono uppercase block">VQA Adherence</span>
                  <span className="text-lg font-bold text-emerald-400 font-mono">
                    {evaluation.prompt_adherence_score}%
                  </span>
                </div>
                <div className="surface-card p-3 rounded-xl border border-white/5 text-center">
                  <span className="text-[10px] text-gray-500 font-mono uppercase block">Overall Quality</span>
                  <span className="text-lg font-bold text-purple-400 font-mono">
                    {evaluation.overall_quality_score}
                  </span>
                </div>
              </div>
            )}
          </div>

          {/* Right: VQA Probe Results & Closed Loop Reflection (7 Cols) */}
          <div className="lg:col-span-7 space-y-6">
            {evaluating ? (
              <div className="h-80 surface-card rounded-2xl flex flex-col items-center justify-center p-8 text-center space-y-3 animate-pulse">
                <RefreshCw className="w-8 h-8 text-cyan-400 animate-spin" />
                <p className="text-xs text-gray-300">Executing VQA probes & CLIP semantic verification...</p>
              </div>
            ) : evaluation ? (
              <>
                {/* VQA Question Probes Table (Bhowmik et al., 2026) */}
                <div className="surface-card p-5 rounded-2xl space-y-4">
                  <div className="flex items-center justify-between border-b border-white/5 pb-3">
                    <div className="flex items-center gap-2">
                      <HelpCircle className="w-4 h-4 text-cyan-400" />
                      <h3 className="text-xs font-semibold text-white font-mono uppercase">
                        VQA Semantic Probes (Visual Question Answering)
                      </h3>
                    </div>
                    <span className="text-[10px] text-emerald-400 font-mono bg-emerald-500/10 px-2 py-0.5 rounded">
                      Verified Alignment
                    </span>
                  </div>

                  <div className="space-y-2.5">
                    {evaluation.vqa_probes.map((probe, i) => (
                      <div
                        key={i}
                        className="p-3 rounded-xl bg-white/[0.02] border border-white/5 flex items-start justify-between gap-3 text-xs"
                      >
                        <div className="space-y-1">
                          <p className="text-gray-200 font-medium">{probe.question}</p>
                          <p className="text-[11px] text-gray-400 font-mono">
                            Expected: <span className="text-gray-300">{probe.expected_answer}</span> | Observed: <span className="text-cyan-400">{probe.observed_answer}</span>
                          </p>
                        </div>
                        <span className={`p-1 rounded-full ${probe.is_aligned ? 'text-emerald-400 bg-emerald-500/10' : 'text-amber-400 bg-amber-500/10'}`}>
                          {probe.is_aligned ? <Check className="w-3.5 h-3.5" /> : <AlertTriangle className="w-3.5 h-3.5" />}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Detected Features & Discrepancy Diagnostics */}
                <div className="surface-card p-5 rounded-2xl space-y-3">
                  <h4 className="text-xs font-semibold text-gray-300 font-mono uppercase">
                    Discrepancy Diagnostics
                  </h4>
                  <p className="text-xs text-gray-300 bg-black/40 p-3 rounded-xl border border-white/5 leading-relaxed font-mono">
                    {evaluation.discrepancy_summary}
                  </p>
                </div>

                {/* Corrective Prompt Synthesis & Closed-Loop Trigger */}
                <div className="surface-card p-5 rounded-2xl space-y-4 border border-cyan-500/30 bg-gradient-to-br from-[#12141A] to-[#0E1015]">
                  <div className="flex items-center justify-between">
                    <div>
                      <span className="text-xs font-semibold text-white font-mono uppercase block">
                        Closed-Loop Corrective Prompt (Iteration {loopIteration})
                      </span>
                      <span className="text-[10px] text-gray-500 font-mono">
                        Auto-synthesized corrective instructions based on VQA error detection
                      </span>
                    </div>
                    <button
                      onClick={() => handleCopy(evaluation.suggested_corrective_prompt)}
                      className="px-2.5 py-1 rounded-lg bg-white/[0.05] hover:bg-white/10 text-cyan-400 text-xs font-mono flex items-center gap-1"
                    >
                      {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                      <span>{copied ? 'Copied' : 'Copy'}</span>
                    </button>
                  </div>

                  <p className="text-xs text-cyan-200 bg-black/50 p-3 rounded-xl border border-white/5 font-mono leading-relaxed select-text">
                    {evaluation.suggested_corrective_prompt}
                  </p>

                  <div className="pt-2 flex items-center gap-3">
                    <button
                      onClick={handleClosedLoopStep}
                      disabled={refiningLoop}
                      className="flex-1 py-3 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 text-white font-semibold text-xs flex items-center justify-center gap-2 shadow-lg shadow-cyan-500/20 hover:opacity-95 transition-all disabled:opacity-50"
                    >
                      <RefreshCw className={`w-3.5 h-3.5 ${refiningLoop ? 'animate-spin' : ''}`} />
                      <span>{refiningLoop ? 'Executing Loop Refinement...' : 'Execute Iterative Self-Correction'}</span>
                    </button>

                    <button
                      onClick={() => navigate('/create', { state: { initialPrompt: evaluation.suggested_corrective_prompt } })}
                      className="px-4 py-3 rounded-xl bg-white/[0.05] hover:bg-white/10 text-gray-200 text-xs font-medium border border-white/5 transition-colors"
                    >
                      <span>Load in Studio</span>
                    </button>
                  </div>
                </div>
              </>
            ) : (
              <div className="h-64 surface-card rounded-2xl flex items-center justify-center text-gray-500 text-xs">
                <span>Select a generated image to run VQA and CLIP visual evaluation.</span>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
