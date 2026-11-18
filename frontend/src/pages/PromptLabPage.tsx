import React, { useState } from 'react';
import {
  FlaskConical,
  Sparkles,
  Sliders,
  Copy,
  Check,
  TrendingUp,
  History,
  Layers,
  ArrowRight,
  GitBranch,
  CheckCircle2
} from 'lucide-react';
import { api } from '../services/api';
import { EvolutionaryOptimizationResult, CandidatePrompt } from '../types';

export const PromptLabPage: React.FC = () => {
  // Input states
  const [initialPrompt, setInitialPrompt] = useState(
    'electric urban motorcycle concept in matte black with carbon fiber frame'
  );
  const [taskType, setTaskType] = useState('industrial_design');
  const [populationSize, setPopulationSize] = useState(6);
  const [numGenerations, setNumGenerations] = useState(3);
  const [mutationRate, setMutationRate] = useState(0.4);
  const [seed, setSeed] = useState(42);

  // Execution states
  const [optimizing, setOptimizing] = useState(false);
  const [optimizationResult, setOptimizationResult] = useState<EvolutionaryOptimizationResult | null>(null);
  const [selectedCandidate, setSelectedCandidate] = useState<CandidatePrompt | null>(null);
  const [selectedGenIndex, setSelectedGenIndex] = useState<number>(0);
  const [copied, setCopied] = useState(false);

  const handleRunOptimization = async () => {
    if (!initialPrompt.trim()) return;
    try {
      setOptimizing(true);
      const res = await api.optimizePrompt({
        initial_prompt: initialPrompt,
        task_type: taskType,
        population_size: populationSize,
        num_generations: numGenerations,
        mutation_rate: mutationRate,
        seed: seed
      });
      setOptimizationResult(res);
      setSelectedGenIndex(res.generation_history.length - 1);
      if (res.generation_history.length > 0) {
        setSelectedCandidate(res.generation_history[res.generation_history.length - 1].candidates[0]);
      }
    } catch (err) {
      console.error('Optimization error', err);
    } finally {
      setOptimizing(false);
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
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-purple-500/10 border border-purple-500/20 text-xs font-mono text-purple-400 mb-2">
          <FlaskConical className="w-3.5 h-3.5" />
          <span>Evolutionary Optimization Engine (APO)</span>
        </div>
        <h1 className="text-2xl font-bold tracking-tight text-white">Prompt Optimization Lab</h1>
        <p className="text-xs text-gray-400 mt-1">
          Perform multi-generation genetic search over prompt space with tournament selection, clause crossover, and reflective mutation.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left Column: Configuration & Baseline Prompt (5 Cols) */}
        <div className="lg:col-span-5 space-y-6">
          {/* Baseline Prompt Input */}
          <div className="surface-card p-5 rounded-2xl space-y-3">
            <div className="flex items-center justify-between">
              <label className="text-xs font-semibold text-gray-300 font-mono uppercase tracking-wide">
                Baseline Manual Prompt (Generation 0)
              </label>
              <span className="text-[10px] text-gray-500 font-mono">Original</span>
            </div>
            <textarea
              rows={4}
              value={initialPrompt}
              onChange={(e) => setInitialPrompt(e.target.value)}
              className="w-full bg-white/[0.03] border border-white/10 rounded-xl p-3 text-xs text-gray-200 font-mono focus:outline-none focus:border-cyan-500/50 resize-y leading-relaxed"
            />
          </div>

          {/* Genetic Algorithm Hyperparameters */}
          <div className="surface-card p-5 rounded-2xl space-y-4">
            <div className="flex items-center gap-2 border-b border-white/5 pb-3">
              <Sliders className="w-4 h-4 text-purple-400" />
              <h3 className="text-xs font-semibold text-white font-mono uppercase">
                Evolutionary Hyperparameters
              </h3>
            </div>

            <div className="space-y-3 text-xs">
              <div>
                <div className="flex justify-between text-gray-400 mb-1">
                  <span>Population Size ($N$)</span>
                  <span className="font-mono text-white">{populationSize} candidates / gen</span>
                </div>
                <input
                  type="range"
                  min="4"
                  max="12"
                  step="2"
                  value={populationSize}
                  onChange={(e) => setPopulationSize(Number(e.target.value))}
                  className="w-full accent-cyan-400"
                />
              </div>

              <div>
                <div className="flex justify-between text-gray-400 mb-1">
                  <span>Number of Generations ($G$)</span>
                  <span className="font-mono text-white">{numGenerations} iterations</span>
                </div>
                <input
                  type="range"
                  min="2"
                  max="6"
                  value={numGenerations}
                  onChange={(e) => setNumGenerations(Number(e.target.value))}
                  className="w-full accent-purple-400"
                />
              </div>

              <div>
                <div className="flex justify-between text-gray-400 mb-1">
                  <span>Mutation Probability ($p_m$)</span>
                  <span className="font-mono text-white">{(mutationRate * 100).toFixed(0)}%</span>
                </div>
                <input
                  type="range"
                  min="0.1"
                  max="0.8"
                  step="0.05"
                  value={mutationRate}
                  onChange={(e) => setMutationRate(Number(e.target.value))}
                  className="w-full accent-cyan-400"
                />
              </div>

              <div className="pt-2 grid grid-cols-2 gap-3">
                <div>
                  <label className="text-gray-400 block mb-1">Random Seed</label>
                  <input
                    type="number"
                    value={seed}
                    onChange={(e) => setSeed(Number(e.target.value))}
                    className="w-full bg-white/[0.03] border border-white/10 rounded-lg p-2 font-mono text-gray-200"
                  />
                </div>
                <div>
                  <label className="text-gray-400 block mb-1">Task Profile</label>
                  <select
                    value={taskType}
                    onChange={(e) => setTaskType(e.target.value)}
                    className="w-full bg-white/[0.03] border border-white/10 rounded-lg p-2 text-gray-200"
                  >
                    <option value="industrial_design">Industrial Design</option>
                    <option value="automotive">Automotive</option>
                    <option value="creative">Creative Art</option>
                  </select>
                </div>
              </div>
            </div>

            <button
              onClick={handleRunOptimization}
              disabled={optimizing || !initialPrompt.trim()}
              className="w-full mt-2 py-3 rounded-xl bg-gradient-to-r from-purple-600 to-indigo-600 hover:opacity-95 text-white text-xs font-semibold flex items-center justify-center gap-2 shadow-lg shadow-purple-500/20 transition-all disabled:opacity-50"
            >
              <Sparkles className={`w-4 h-4 ${optimizing ? 'animate-spin' : ''}`} />
              <span>{optimizing ? 'Executing Genetic Search...' : 'Execute Evolutionary Optimization'}</span>
            </button>
          </div>
        </div>

        {/* Right Column: Evolutionary Trajectory & Candidate Inspection (7 Cols) */}
        <div className="lg:col-span-7 space-y-6">
          {optimizationResult ? (
            <>
              {/* Fitness Improvement Score Banner */}
              <div className="surface-card p-5 rounded-2xl border-l-4 border-l-emerald-500 flex items-center justify-between">
                <div>
                  <span className="text-[11px] text-gray-400 font-mono uppercase tracking-wider block">
                    Pareto Optimization Summary
                  </span>
                  <div className="flex items-baseline gap-3 mt-1">
                    <span className="text-2xl font-bold text-white font-mono">
                      {optimizationResult.best_fitness.toFixed(3)}
                    </span>
                    <span className="text-xs text-gray-500 font-mono">
                      from baseline {optimizationResult.initial_fitness.toFixed(3)}
                    </span>
                  </div>
                </div>

                <div className="text-right">
                  <span className="px-3 py-1 rounded-xl bg-emerald-500/15 border border-emerald-500/30 text-emerald-400 text-xs font-mono font-bold flex items-center gap-1">
                    <TrendingUp className="w-3.5 h-3.5" />
                    +{optimizationResult.improvement_percentage}%
                  </span>
                  <span className="text-[10px] text-gray-500 mt-1 block">across {optimizationResult.total_generations} generations</span>
                </div>
              </div>

              {/* Generation Timeline Tabs */}
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-semibold text-gray-300 font-mono uppercase">
                    Generation Lineage
                  </span>
                  <span className="text-[11px] text-gray-500 font-mono">Select generation to view population</span>
                </div>

                <div className="flex items-center gap-2 overflow-x-auto pb-1">
                  {optimizationResult.generation_history.map((gen, idx) => (
                    <button
                      key={idx}
                      onClick={() => {
                        setSelectedGenIndex(idx);
                        setSelectedCandidate(gen.candidates[0]);
                      }}
                      className={`px-3 py-1.5 rounded-xl text-xs font-mono transition-all ${
                        selectedGenIndex === idx
                          ? 'bg-purple-500/20 text-purple-300 border border-purple-500/50 font-bold'
                          : 'bg-white/[0.03] text-gray-400 border border-white/5 hover:text-white'
                      }`}
                    >
                      Gen {gen.generation_index} ({gen.best_fitness.toFixed(2)})
                    </button>
                  ))}
                </div>
              </div>

              {/* Candidates in Current Generation */}
              <div className="surface-card p-5 rounded-2xl space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-semibold text-gray-200 font-mono">
                    Generation {selectedGenIndex} Population Candidates ({optimizationResult.generation_history[selectedGenIndex].candidates.length})
                  </span>
                </div>

                <div className="space-y-2 max-h-56 overflow-y-auto pr-1">
                  {optimizationResult.generation_history[selectedGenIndex].candidates.map((cand) => (
                    <div
                      key={cand.candidate_id}
                      onClick={() => setSelectedCandidate(cand)}
                      className={`p-3 rounded-xl border text-xs cursor-pointer transition-all ${
                        selectedCandidate?.candidate_id === cand.candidate_id
                          ? 'bg-purple-500/10 border-purple-500/40 text-white'
                          : 'bg-white/[0.02] border-white/5 text-gray-300 hover:bg-white/[0.04]'
                      }`}
                    >
                      <div className="flex items-center justify-between mb-1">
                        <span className="font-mono text-cyan-400 font-medium">{cand.candidate_id}</span>
                        <span className="font-mono text-[11px] text-gray-400">
                          Fitness: <span className="text-emerald-400 font-bold">{cand.fitness_score}</span>
                        </span>
                      </div>
                      <p className="line-clamp-2 text-gray-300 font-mono text-[11px] leading-relaxed">
                        {cand.prompt}
                      </p>
                    </div>
                  ))}
                </div>
              </div>

              {/* Selected Candidate Deep Inspection */}
              {selectedCandidate && (
                <div className="surface-card p-5 rounded-2xl space-y-4 border border-cyan-500/20 bg-gradient-to-b from-[#13151B] to-[#0E1014]">
                  <div className="flex items-center justify-between">
                    <div>
                      <span className="text-xs font-semibold text-white font-mono">
                        Candidate Inspection: {selectedCandidate.candidate_id}
                      </span>
                      <span className="text-[10px] text-gray-500 block font-mono">
                        Mutation: {selectedCandidate.mutation_type || 'None'} | Parents: {selectedCandidate.parent_ids.join(', ')}
                      </span>
                    </div>

                    <button
                      onClick={() => handleCopy(selectedCandidate.prompt)}
                      className="px-2.5 py-1 rounded-lg bg-white/[0.05] hover:bg-white/10 text-cyan-400 text-xs font-mono flex items-center gap-1"
                    >
                      {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                      <span>{copied ? 'Copied' : 'Copy Prompt'}</span>
                    </button>
                  </div>

                  <p className="text-xs text-cyan-200 bg-black/40 p-3 rounded-xl border border-white/5 font-mono leading-relaxed select-text">
                    {selectedCandidate.prompt}
                  </p>

                  {/* Metrics Radar Breakdown */}
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 pt-2 border-t border-white/5 text-[11px] font-mono">
                    {Object.entries(selectedCandidate.metrics).map(([metricName, val]) => (
                      <div key={metricName} className="p-2 rounded-lg bg-white/[0.02] border border-white/5">
                        <span className="text-gray-500 text-[10px] block truncate capitalize">
                          {metricName.replace(/_/g, ' ')}
                        </span>
                        <span className="text-gray-200 font-bold text-xs">{val}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </>
          ) : (
            <div className="h-96 surface-card rounded-2xl border-dashed border-white/10 flex flex-col items-center justify-center p-8 text-center space-y-3 text-gray-500">
              <FlaskConical className="w-10 h-10 text-gray-600" />
              <p className="text-sm">Configure parameters on the left and run the evolutionary genetic search.</p>
              <p className="text-xs text-gray-600 max-w-sm">
                The algorithm will generate populations, score objective fitness, apply crossover of prompt clauses, and mutate candidates across iterations.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
