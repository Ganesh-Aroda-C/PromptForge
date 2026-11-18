import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Settings,
  Key,
  CheckCircle2,
  Save,
  Check,
  FlaskConical,
  Eye,
  Database,
  ArrowRight,
  Shield
} from 'lucide-react';
import { api } from '../services/api';
import { SystemStatus } from '../types';

interface SettingsPageProps {
  systemStatus: SystemStatus | null;
  onRefreshStatus: () => void;
}

export const SettingsPage: React.FC<SettingsPageProps> = ({ systemStatus, onRefreshStatus }) => {
  const navigate = useNavigate();
  const [geminiKey, setGeminiKey] = useState('');
  const [openaiKey, setOpenaiKey] = useState('');
  const [hfKey, setHfKey] = useState('');
  const [llmProvider, setLlmProvider] = useState('mock');
  const [diffusionProvider, setDiffusionProvider] = useState('demo');
  const [saved, setSaved] = useState(false);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.updateSettings({
        llm_provider: llmProvider,
        diffusion_provider: diffusionProvider,
        gemini_api_key: geminiKey,
        openai_api_key: openaiKey,
        huggingface_api_key: hfKey
      });
      setSaved(true);
      setTimeout(() => setSaved(false), 2500);
      onRefreshStatus();
    } catch (err) {
      console.error('Failed to update settings', err);
    }
  };

  return (
    <div className="space-y-10 animate-fadeIn max-w-4xl mx-auto pb-16">
      {/* Header */}
      <div className="border-b border-white/5 pb-6">
        <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2.5">
          <Settings className="w-6 h-6 text-cyan-400" />
          <span>Settings</span>
        </h1>
        <p className="text-xs text-gray-400 mt-1">
          Manage AI providers, model preferences, and access research tools.
        </p>
      </div>

      {/* Separate Research & Admin Area (Moved out of main navigation) */}
      <div className="surface-card p-6 rounded-3xl border border-white/10 space-y-4 bg-gradient-to-br from-[#12141A] to-[#0D0F14]">
        <div className="flex items-center justify-between border-b border-white/5 pb-3">
          <div className="flex items-center gap-2">
            <Shield className="w-4 h-4 text-cyan-400" />
            <h2 className="text-sm font-semibold text-white">Research & Evaluation Suite</h2>
          </div>
          <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-white/5 text-gray-400">
            Admin & Analysis Tools
          </span>
        </div>

        <p className="text-xs text-gray-400 leading-relaxed">
          Access algorithmic experimentation modules, evolutionary prompt optimization, visual evaluation metrics, and benchmark datasets.
        </p>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-1">
          {/* Prompt Lab Link */}
          <div
            onClick={() => navigate('/prompt-lab')}
            className="p-4 rounded-2xl bg-white/[0.03] hover:bg-white/[0.06] border border-white/5 hover:border-cyan-500/40 cursor-pointer transition-all space-y-2 group"
          >
            <div className="flex items-center justify-between">
              <FlaskConical className="w-5 h-5 text-purple-400 group-hover:scale-110 transition-transform" />
              <ArrowRight className="w-3.5 h-3.5 text-gray-500 group-hover:text-cyan-400 group-hover:translate-x-0.5 transition-all" />
            </div>
            <h3 className="text-xs font-semibold text-white">Prompt Lab</h3>
            <p className="text-[11px] text-gray-400 leading-snug">
              Evolutionary algorithm search, Pareto fitness trajectories, and prompt mutations.
            </p>
          </div>

          {/* Evaluation Link */}
          <div
            onClick={() => navigate('/evaluation')}
            className="p-4 rounded-2xl bg-white/[0.03] hover:bg-white/[0.06] border border-white/5 hover:border-cyan-500/40 cursor-pointer transition-all space-y-2 group"
          >
            <div className="flex items-center justify-between">
              <Eye className="w-5 h-5 text-cyan-400 group-hover:scale-110 transition-transform" />
              <ArrowRight className="w-3.5 h-3.5 text-gray-500 group-hover:text-cyan-400 group-hover:translate-x-0.5 transition-all" />
            </div>
            <h3 className="text-xs font-semibold text-white">Visual Evaluation</h3>
            <p className="text-[11px] text-gray-400 leading-snug">
              VQA probe questions, semantic alignment, and closed-loop feedback correction.
            </p>
          </div>

          {/* Dataset Studio Link */}
          <div
            onClick={() => navigate('/datasets')}
            className="p-4 rounded-2xl bg-white/[0.03] hover:bg-white/[0.06] border border-white/5 hover:border-cyan-500/40 cursor-pointer transition-all space-y-2 group"
          >
            <div className="flex items-center justify-between">
              <Database className="w-5 h-5 text-emerald-400 group-hover:scale-110 transition-transform" />
              <ArrowRight className="w-3.5 h-3.5 text-gray-500 group-hover:text-cyan-400 group-hover:translate-x-0.5 transition-all" />
            </div>
            <h3 className="text-xs font-semibold text-white">Dataset Studio</h3>
            <p className="text-[11px] text-gray-400 leading-snug">
              Manage benchmark datasets (V-LAB, IDD, DrawBench) and export JSON/CSV records.
            </p>
          </div>
        </div>
      </div>

      {/* Model Providers & API Keys Configuration Form */}
      <div className="surface-card p-6 sm:p-8 rounded-3xl border border-white/10 space-y-6">
        <div className="flex items-center gap-2 border-b border-white/5 pb-4">
          <Key className="w-4 h-4 text-cyan-400" />
          <h2 className="text-sm font-semibold text-white">AI Provider Settings</h2>
        </div>

        <form onSubmit={handleSave} className="space-y-5 text-xs">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="text-gray-300 block mb-1 font-medium">Text Analysis & Prompt Engine</label>
              <select
                value={llmProvider}
                onChange={(e) => setLlmProvider(e.target.value)}
                className="w-full bg-white/[0.04] border border-white/10 rounded-xl p-3 text-white"
              >
                <option value="mock">Automatic Built-in Engine (Default)</option>
                <option value="openai">OpenAI (GPT-4o)</option>
                <option value="gemini">Google Gemini</option>
                <option value="huggingface">Hugging Face API</option>
              </select>
            </div>

            <div>
              <label className="text-gray-300 block mb-1 font-medium">Image Generation Engine</label>
              <select
                value={diffusionProvider}
                onChange={(e) => setDiffusionProvider(e.target.value)}
                className="w-full bg-white/[0.04] border border-white/10 rounded-xl p-3 text-white"
              >
                <option value="demo">High-Resolution Concept Engine (Default)</option>
                <option value="huggingface">Hugging Face Diffusion API</option>
                <option value="openai">OpenAI DALL-E 3</option>
              </select>
            </div>
          </div>

          <div className="space-y-3 pt-1">
            <div>
              <label className="text-gray-400 block mb-1">OpenAI API Key (Optional)</label>
              <input
                type="password"
                value={openaiKey}
                onChange={(e) => setOpenaiKey(e.target.value)}
                placeholder="sk-..."
                className="w-full bg-white/[0.03] border border-white/10 rounded-xl p-3 text-white font-mono"
              />
            </div>

            <div>
              <label className="text-gray-400 block mb-1">Google Gemini API Key (Optional)</label>
              <input
                type="password"
                value={geminiKey}
                onChange={(e) => setGeminiKey(e.target.value)}
                placeholder="AIzaSy..."
                className="w-full bg-white/[0.03] border border-white/10 rounded-xl p-3 text-white font-mono"
              />
            </div>

            <div>
              <label className="text-gray-400 block mb-1">Hugging Face Token (Optional)</label>
              <input
                type="password"
                value={hfKey}
                onChange={(e) => setHfKey(e.target.value)}
                placeholder="hf_..."
                className="w-full bg-white/[0.03] border border-white/10 rounded-xl p-3 text-white font-mono"
              />
            </div>
          </div>

          <div className="flex items-center justify-between pt-4 border-t border-white/5">
            <span className="text-[11px] text-gray-500">
              API keys are stored securely on your server and never exposed in browser code.
            </span>
            <button
              type="submit"
              className="px-6 py-2.5 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-black font-semibold text-xs flex items-center gap-1.5 transition-colors cursor-pointer"
            >
              {saved ? <Check className="w-3.5 h-3.5" /> : <Save className="w-3.5 h-3.5" />}
              <span>{saved ? 'Saved' : 'Save Settings'}</span>
            </button>
          </div>
        </form>
      </div>

      {/* Simple Footer */}
      <div className="surface-card p-5 rounded-2xl border border-white/5 text-xs text-gray-400 space-y-1">
        <p className="font-semibold text-white">PromptForge AI</p>
        <p className="text-[11px] text-gray-500">
          Professional generative design platform for industrial products, visual concepts, and creative prototyping.
        </p>
      </div>
    </div>
  );
};
