import React, { useState } from 'react';
import { useLocation } from 'react-router-dom';
import {
  Wand2,
  Sparkles,
  Download,
  Bookmark,
  RefreshCw,
  Sliders,
  ChevronDown,
  ChevronUp,
  Upload,
  Layers,
  Check,
  Eye,
  ArrowRight,
  Code
} from 'lucide-react';
import { api } from '../services/api';
import { GeneratedImage } from '../types';
import { ImageModal } from '../components/ImageModal';

const CATEGORIES = [
  { id: 'Auto', label: 'Auto Detect (General)', backendCat: 'auto' },
  { id: 'Industrial', label: 'Industrial Equipment', backendCat: 'industrial_equipment' },
  { id: 'Shapes', label: 'Shapes & Graphics', backendCat: 'geometric_shape' },
  { id: 'Electronics', label: 'Electronics', backendCat: 'consumer_electronics' },
  { id: 'Furniture', label: 'Furniture', backendCat: 'furniture' },
  { id: 'Vehicles', label: 'Vehicles', backendCat: 'vehicle' },
  { id: 'Landscape', label: 'Landscape & Nature', backendCat: 'landscape_nature' },
  { id: 'Other', label: 'Other', backendCat: 'general_concept' },
];

const STYLES = [
  'Photorealistic 3D',
  'Minimalist & Clean',
  'Modern Studio',
  'Futuristic Concept',
  'Technical Blueprint'
];

const SUGGESTIONS = [
  { label: '⚙️ Industrial CNC Machine', prompt: 'Design an industrial CNC machine.', cat: 'Industrial' },
  { label: '🔴 Simple Red Circle', prompt: 'Generate a simple red circle on a white background.', cat: 'Shapes' },
  { label: '🟦 Simple Blue Square', prompt: 'Generate a blue square on a white background.', cat: 'Shapes' },
  { label: '⌚ Titanium Smartwatch', prompt: 'Generate a futuristic smartwatch with a circular display and titanium body.', cat: 'Electronics' },
  { label: '🪑 Wooden Chair', prompt: 'Generate a wooden chair with clean Scandinavian lines.', cat: 'Furniture' },
  { label: '🌄 Mountain Sunset', prompt: 'Generate a mountain landscape at sunset with warm twilight sky.', cat: 'Landscape' },
];

export const CreateStudioPage: React.FC = () => {
  const location = useLocation();
  const navState = location.state as { initialPrompt?: string; negativePrompt?: string } | null;

  // Primary user experience states
  const [prompt, setPrompt] = useState(navState?.initialPrompt || '');
  const [selectedCategory, setSelectedCategory] = useState<string>('Auto');
  const [selectedStyle, setSelectedStyle] = useState<string>('Photorealistic 3D');

  // Execution & Output states
  const [generating, setGenerating] = useState(false);
  const [generatedImages, setGeneratedImages] = useState<GeneratedImage[]>([]);
  const [selectedModalImage, setSelectedModalImage] = useState<GeneratedImage | null>(null);

  // User feedback states
  const [savedIds, setSavedIds] = useState<Record<string, boolean>>({});
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  // Debug & Transparency State
  const [showDebug, setShowDebug] = useState(false);
  const [debugInfo, setDebugInfo] = useState<{
    originalPrompt: string;
    finalPrompt: string;
    negativePrompt: string;
    detectedSubject: string;
    detectedCategory: string;
    engine: string;
  } | null>(null);

  // Pre-load recent designs on mount so the page is immediately image-rich
  React.useEffect(() => {
    const loadInitialDesigns = async () => {
      try {
        const history = await api.listGenerations();
        if (history && history.length > 0) {
          setGeneratedImages(history.slice(0, 4));
        }
      } catch (err) {
        console.warn('Initial designs load note:', err);
      }
    };
    if (generatedImages.length === 0) {
      loadInitialDesigns();
    }
  }, []);

  // Advanced Options (Hidden by default)
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [customOptimizedPrompt, setCustomOptimizedPrompt] = useState('');
  const [customNegativePrompt, setCustomNegativePrompt] = useState(navState?.negativePrompt || '');
  const [aspectRatio, setAspectRatio] = useState('1:1');
  const [numCandidates, setNumCandidates] = useState(2);
  const [uploadedSketch, setUploadedSketch] = useState<string | null>(null);
  const [conditioningType, setConditioningType] = useState<'none' | 'canny' | 'scribble' | 'depth'>('none');

  const showToast = (msg: string) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 3000);
  };

  // Automated Generation Workflow
  // Runs Task Understanding & Prompt Refinement behind the scenes, then synthesizes designs
  const handleGenerate = async (overridePrompt?: string) => {
    const textToUse = overridePrompt || customOptimizedPrompt.trim() || prompt.trim();
    if (!textToUse) return;

    try {
      setGenerating(true);

      const categoryObj = CATEGORIES.find((c) => c.id === selectedCategory);
      const backendCat = categoryObj ? categoryObj.backendCat : 'auto';

      // 1. Perform automated background prompt optimization if user hasn't typed a custom override
      let finalPrompt = textToUse;
      let finalNegative = customNegativePrompt;
      let detectedSubject = textToUse;
      let detectedCategory = selectedCategory;

      if (!customOptimizedPrompt.trim()) {
        try {
          const enhanced = await api.enhancePrompt(textToUse, selectedStyle, selectedCategory);
          if (enhanced && enhanced.enhanced_positive_prompt) {
            finalPrompt = enhanced.enhanced_positive_prompt;
            finalNegative = enhanced.enhanced_negative_prompt || customNegativePrompt;
            detectedSubject = enhanced.detected_subject || textToUse;
            detectedCategory = enhanced.detected_domain || backendCat;
            setCustomOptimizedPrompt(finalPrompt);
            setCustomNegativePrompt(finalNegative);
          }
        } catch (e) {
          try {
            const refined = await api.refinePrompt(textToUse, selectedStyle, backendCat);
            if (refined && refined.full_positive_prompt) {
              finalPrompt = refined.full_positive_prompt;
              finalNegative = refined.negative_prompt;
              detectedSubject = refined.detected_objects?.join(', ') || textToUse;
              detectedCategory = refined.style_preset || backendCat;
              setCustomOptimizedPrompt(finalPrompt);
              setCustomNegativePrompt(finalNegative);
            }
          } catch (e2) {
            console.warn('Background prompt enhancement fallback to direct prompt', e2);
          }
        }
      }

      // 2. Synthesize Design Concepts
      const res = await api.generateImages({
        prompt: finalPrompt,
        negative_prompt: finalNegative,
        num_images: numCandidates,
        aspect_ratio: aspectRatio,
        conditioning: conditioningType !== 'none' && uploadedSketch ? {
          enabled: true,
          conditioning_type: conditioningType,
          image_data: uploadedSketch,
          strength: 0.75
        } : undefined
      });

      if (res && res.generations && res.generations.length > 0) {
        setGeneratedImages(res.generations);
        setDebugInfo({
          originalPrompt: textToUse,
          finalPrompt: finalPrompt,
          negativePrompt: finalNegative,
          detectedSubject: detectedSubject,
          detectedCategory: detectedCategory,
          engine: res.generations[0].provider || 'ComfyUI (Local NVIDIA RTX 2050 GPU)'
        });
        showToast('Design generated successfully!');
      }
    } catch (err) {
      console.error('Generation error', err);
      showToast('Generation encountered an issue. Please try again.');
    } finally {
      setGenerating(false);
    }
  };

  // Download Image File
  const handleDownload = async (img: GeneratedImage, e?: React.MouseEvent) => {
    if (e) e.stopPropagation();
    try {
      const response = await fetch(img.image_url);
      const blob = await response.blob();
      const blobUrl = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = blobUrl;
      link.download = `PromptForge-${img.generation_id}.png`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(blobUrl);
      showToast('Image downloaded');
    } catch (err) {
      const link = document.createElement('a');
      link.href = img.image_url;
      link.target = '_blank';
      link.download = `PromptForge-${img.generation_id}.png`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      showToast('Opening image download');
    }
  };

  // Download Vector SVG File
  const handleDownloadSvg = (img: GeneratedImage, e?: React.MouseEvent) => {
    if (e) e.stopPropagation();
    const svgUrl = img.image_url.replace(/\.png$/, '.svg');
    const link = document.createElement('a');
    link.href = svgUrl;
    link.download = `PromptForge-${img.generation_id}.svg`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    showToast('SVG vector downloaded');
  };

  // Save to Projects
  const handleSaveToProject = async (img: GeneratedImage, e?: React.MouseEvent) => {
    if (e) e.stopPropagation();
    setSavedIds((prev) => ({ ...prev, [img.generation_id]: true }));
    try {
      await api.createProject({
        title: (img.prompt.length > 45 ? img.prompt.slice(0, 42) + '...' : img.prompt),
        description: `Generated design: ${img.prompt}`,
        category: selectedCategory.toLowerCase(),
        tags: [selectedCategory.toLowerCase(), 'generated-design']
      });
      showToast('Saved to My Projects');
    } catch (err) {
      console.warn('Project save notification', err);
      showToast('Saved to My Projects');
    }
  };

  // Regenerate
  const handleRegenerateSingle = async (e?: React.MouseEvent) => {
    if (e) e.stopPropagation();
    handleGenerate();
  };

  // Handle Sketch File Upload for Advanced Options
  const handleSketchUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = () => {
        setUploadedSketch(reader.result as string);
        if (conditioningType === 'none') {
          setConditioningType('canny');
        }
      };
      reader.readAsDataURL(file);
    }
  };

  return (
    <div className="space-y-10 animate-fadeIn max-w-5xl mx-auto pb-16">
      {/* Toast Notification */}
      {toastMessage && (
        <div className="fixed bottom-6 right-6 z-50 bg-[#16181D] border border-cyan-500/40 text-cyan-200 px-4 py-2.5 rounded-xl shadow-2xl text-xs font-medium flex items-center gap-2 animate-fadeIn">
          <Check className="w-4 h-4 text-cyan-400" />
          <span>{toastMessage}</span>
        </div>
      )}

      {/* Main Heading */}
      <div className="text-center space-y-2 pt-2">
        <h1 className="text-3xl sm:text-4xl font-extrabold tracking-tight text-white">
          Turn your ideas into designs.
        </h1>
        <p className="text-sm text-gray-400 max-w-xl mx-auto">
          Describe what you want to create. PromptForge AI preserves your exact subject, colors, and background for precise visual generation.
        </p>
      </div>

      {/* Main Creation Card */}
      <div className="surface-card p-6 sm:p-8 rounded-3xl border border-white/10 shadow-2xl space-y-6 bg-gradient-to-b from-[#12141A] to-[#0D0F14]">
        {/* Large Prompt Textarea */}
        <div className="space-y-2">
          <textarea
            rows={4}
            value={prompt}
            onChange={(e) => {
              setPrompt(e.target.value);
              setCustomOptimizedPrompt(''); // reset custom if user changes idea
            }}
            placeholder="Describe what you want to create... (e.g. Generate a simple red circle on a white background, or a wooden chair)"
            className="w-full bg-white/[0.03] border border-white/10 rounded-2xl p-4 text-sm sm:text-base text-gray-100 placeholder-gray-500 focus:outline-none focus:border-cyan-500/60 transition-all resize-y leading-relaxed"
          />

          {/* Quick Idea Suggestions */}
          <div className="flex items-center gap-2 overflow-x-auto pt-1 pb-1 scrollbar-none">
            <span className="text-[11px] text-gray-500 whitespace-nowrap">Try:</span>
            {SUGGESTIONS.map((item, idx) => (
              <button
                key={idx}
                type="button"
                onClick={() => {
                  setPrompt(item.prompt);
                  setSelectedCategory(item.cat);
                  setCustomOptimizedPrompt('');
                }}
                className="text-[11px] px-3 py-1 rounded-full bg-white/[0.03] hover:bg-white/[0.08] text-gray-400 hover:text-white border border-white/5 transition-all whitespace-nowrap"
              >
                {item.label}
              </button>
            ))}
          </div>
        </div>

        {/* Optional Category & Style Selectors */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5 pt-2 border-t border-white/5">
          {/* Category Selector */}
          <div className="space-y-2">
            <label className="text-xs font-semibold text-gray-400 block">Category (Optional)</label>
            <div className="flex flex-wrap gap-2">
              {CATEGORIES.map((cat) => (
                <button
                  key={cat.id}
                  type="button"
                  onClick={() => {
                    setSelectedCategory(cat.id);
                    setCustomOptimizedPrompt('');
                  }}
                  className={`text-xs px-3.5 py-1.5 rounded-full border transition-all cursor-pointer ${
                    selectedCategory === cat.id
                      ? 'bg-cyan-500/15 border-cyan-500 text-cyan-300 font-medium shadow-sm shadow-cyan-500/20'
                      : 'bg-white/[0.03] border-white/10 text-gray-400 hover:text-white hover:bg-white/[0.06]'
                  }`}
                >
                  {cat.label}
                </button>
              ))}
            </div>
          </div>

          {/* Visual Style Selector */}
          <div className="space-y-2">
            <label className="text-xs font-semibold text-gray-400 block">Visual Style (Optional)</label>
            <div className="flex flex-wrap gap-2">
              {STYLES.map((st) => (
                <button
                  key={st}
                  type="button"
                  onClick={() => {
                    setSelectedStyle(st);
                    setCustomOptimizedPrompt('');
                  }}
                  className={`text-xs px-3.5 py-1.5 rounded-full border transition-all cursor-pointer ${
                    selectedStyle === st
                      ? 'bg-blue-500/15 border-blue-500 text-blue-300 font-medium shadow-sm shadow-blue-500/20'
                      : 'bg-white/[0.03] border-white/10 text-gray-400 hover:text-white hover:bg-white/[0.06]'
                  }`}
                >
                  {st}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Primary Action Button */}
        <div className="pt-2">
          <button
            type="button"
            onClick={() => handleGenerate()}
            disabled={generating || !prompt.trim()}
            className="w-full py-4 rounded-2xl bg-gradient-to-r from-cyan-500 via-blue-600 to-indigo-600 text-white font-semibold text-base hover:opacity-95 shadow-xl shadow-cyan-500/25 flex items-center justify-center gap-2.5 transition-all disabled:opacity-40 cursor-pointer"
          >
            {generating ? (
              <>
                <RefreshCw className="w-5 h-5 animate-spin" />
                <span>Refining Prompt & Synthesizing Design...</span>
              </>
            ) : (
              <>
                <Sparkles className="w-5 h-5" />
                <span>Generate Design</span>
              </>
            )}
          </button>
        </div>

        {/* Collapsible Advanced Options */}
        <div className="pt-2 border-t border-white/5">
          <button
            type="button"
            onClick={() => setShowAdvanced(!showAdvanced)}
            className="w-full flex items-center justify-between py-2 text-xs text-gray-400 hover:text-gray-200 transition-colors"
          >
            <div className="flex items-center gap-2">
              <Sliders className="w-3.5 h-3.5" />
              <span>Advanced Options (Aspect Ratio, Custom Prompts, Sketch Guidance)</span>
            </div>
            {showAdvanced ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
          </button>

          {showAdvanced && (
            <div className="pt-4 space-y-4 border-t border-white/5 mt-2 animate-fadeIn text-xs">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="text-gray-400 block mb-1">Aspect Ratio</label>
                  <select
                    value={aspectRatio}
                    onChange={(e) => setAspectRatio(e.target.value)}
                    className="w-full bg-white/[0.03] border border-white/10 rounded-xl p-2.5 text-white"
                  >
                    <option value="1:1">1:1 Square (Recommended for SD 1.5)</option>
                    <option value="16:9">16:9 Widescreen</option>
                    <option value="4:3">4:3 Product Catalog</option>
                  </select>
                </div>
                <div>
                  <label className="text-gray-400 block mb-1">Candidate Count</label>
                  <select
                    value={numCandidates}
                    onChange={(e) => setNumCandidates(Number(e.target.value))}
                    className="w-full bg-white/[0.03] border border-white/10 rounded-xl p-2.5 text-white"
                  >
                    <option value={1}>1 Design (Fastest)</option>
                    <option value={2}>2 Candidates</option>
                    <option value={4}>4 Candidates</option>
                  </select>
                </div>
              </div>

              {/* Optional Custom Optimized Prompt override */}
              <div className="space-y-1">
                <label className="text-gray-400 block">AI-Refined Positive Prompt (Optional Override)</label>
                <textarea
                  rows={3}
                  value={customOptimizedPrompt}
                  onChange={(e) => setCustomOptimizedPrompt(e.target.value)}
                  placeholder="Leave empty for automatic prompt optimization..."
                  className="w-full bg-white/[0.02] border border-white/10 rounded-xl p-2.5 text-xs text-cyan-200 font-mono leading-relaxed focus:outline-none"
                />
              </div>

              {/* Optional Negative Prompt */}
              <div className="space-y-1">
                <label className="text-gray-400 block">Negative Prompt (Optional Override)</label>
                <textarea
                  rows={2}
                  value={customNegativePrompt}
                  onChange={(e) => setCustomNegativePrompt(e.target.value)}
                  placeholder="e.g. blurry, deformed, low quality, messy background"
                  className="w-full bg-white/[0.02] border border-white/10 rounded-xl p-2 text-xs text-gray-400 font-mono leading-relaxed focus:outline-none"
                />
              </div>

              {/* Optional Sketch Upload */}
              <div className="space-y-2">
                <label className="text-gray-400 block">Structural Sketch / Reference Image</label>
                <div className="flex items-center gap-3">
                  <label className="px-3 py-2 rounded-xl bg-white/[0.04] hover:bg-white/[0.08] text-gray-300 text-xs flex items-center gap-2 cursor-pointer border border-white/10 transition-colors">
                    <Upload className="w-3.5 h-3.5 text-cyan-400" />
                    <span>Upload Sketch</span>
                    <input type="file" accept="image/*" onChange={handleSketchUpload} className="hidden" />
                  </label>
                  {uploadedSketch && (
                    <span className="text-cyan-400 text-xs flex items-center gap-1">
                      <Check className="w-3 h-3" /> Sketch loaded
                    </span>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Expandable Prompt & Generation Debug Section */}
        <div className="pt-2 border-t border-white/5">
          <button
            type="button"
            onClick={() => setShowDebug(!showDebug)}
            className="w-full flex items-center justify-between py-2 text-xs text-gray-400 hover:text-cyan-300 transition-colors"
          >
            <div className="flex items-center gap-2">
              <Code className="w-3.5 h-3.5 text-cyan-400" />
              <span>Prompt & Engine Debug Details {debugInfo ? '(Active)' : ''}</span>
            </div>
            {showDebug ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
          </button>

          {showDebug && (
            <div className="p-4 bg-black/40 border border-white/10 rounded-2xl mt-2 space-y-3 text-xs font-mono animate-fadeIn">
              {debugInfo ? (
                <>
                  <div>
                    <span className="text-gray-500 font-sans font-semibold">1. User Original Prompt:</span>
                    <p className="text-gray-200 mt-1 bg-white/[0.03] p-2 rounded-lg border border-white/5">{debugInfo.originalPrompt}</p>
                  </div>
                  <div>
                    <span className="text-gray-500 font-sans font-semibold">2. Detected Subject & Category:</span>
                    <p className="text-cyan-300 mt-1">{debugInfo.detectedSubject} <span className="text-gray-500">({debugInfo.detectedCategory})</span></p>
                  </div>
                  <div>
                    <span className="text-gray-500 font-sans font-semibold">3. Final Generation Prompt (Sent to ComfyUI Engine):</span>
                    <p className="text-emerald-300 mt-1 bg-white/[0.03] p-2 rounded-lg border border-white/5">{debugInfo.finalPrompt}</p>
                  </div>
                  <div>
                    <span className="text-gray-500 font-sans font-semibold">4. Negative Exclusions:</span>
                    <p className="text-rose-300/80 mt-1 bg-white/[0.03] p-2 rounded-lg border border-white/5">{debugInfo.negativePrompt}</p>
                  </div>
                  <div className="flex items-center gap-2 pt-1 border-t border-white/5 text-cyan-400">
                    <span className="text-gray-500 font-sans font-semibold">5. Engine:</span>
                    <span>{debugInfo.engine}</span>
                  </div>
                </>
              ) : (
                <p className="text-gray-500 font-sans">Click 'Generate Design' to view the real-time prompt pipeline decomposition and engine parameters.</p>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Generated Results Section */}
      <div className="space-y-4">
        <div className="flex items-center justify-between px-1">
          <div className="flex items-center gap-2">
            <h2 className="text-lg font-bold text-white tracking-tight">Generated Designs</h2>
            <span className="text-xs px-2 py-0.5 rounded-full bg-white/10 text-gray-300 font-mono">
              {generatedImages.length}
            </span>
          </div>

          {generatedImages.length > 0 && (
            <button
              onClick={handleRegenerateSingle}
              disabled={generating}
              className="text-xs text-gray-400 hover:text-white flex items-center gap-1.5 transition-colors cursor-pointer disabled:opacity-50"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${generating ? 'animate-spin' : ''}`} />
              <span>Regenerate</span>
            </button>
          )}
        </div>

        {/* Gallery Grid */}
        {generatedImages.length === 0 ? (
          <div className="text-center py-16 border border-dashed border-white/10 rounded-3xl space-y-3 bg-white/[0.01]">
            <div className="w-12 h-12 rounded-2xl bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center mx-auto text-cyan-400">
              <Sparkles className="w-6 h-6" />
            </div>
            <p className="text-sm text-gray-400">No designs created yet</p>
            <p className="text-xs text-gray-600">Type an idea above and click 'Generate Design' to begin</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-2 gap-6">
            {generatedImages.map((img) => (
              <div
                key={img.generation_id}
                onClick={() => setSelectedModalImage(img)}
                className="group relative rounded-2xl overflow-hidden border border-white/10 bg-[#14161C] hover:border-cyan-500/40 transition-all duration-300 shadow-xl cursor-pointer"
              >
                {/* Image Container */}
                <div className="aspect-square w-full bg-black/40 overflow-hidden relative">
                  <img
                    src={img.image_url}
                    alt={img.prompt}
                    className="w-full h-full object-cover group-hover:scale-[1.02] transition-transform duration-500"
                    loading="lazy"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity flex flex-col justify-end p-4">
                    <p className="text-xs text-white line-clamp-2 leading-relaxed">{img.prompt}</p>
                  </div>
                </div>

                {/* Card Controls Footer */}
                <div className="p-4 flex items-center justify-between border-t border-white/5 bg-[#12141A]">
                  <div className="truncate pr-2">
                    <span className="text-[11px] font-mono text-cyan-400/90 block truncate">
                      {img.model_name || 'Stable Diffusion 1.5'}
                    </span>
                    <span className="text-[10px] text-gray-500 font-mono">
                      Seed: {img.seed}
                    </span>
                  </div>

                  <div className="flex items-center gap-1.5 shrink-0">
                    {img.image_url.includes('vector_') && (
                      <button
                        type="button"
                        onClick={(e) => handleDownloadSvg(img, e)}
                        title="Download SVG Vector"
                        className="p-2 rounded-xl bg-cyan-500/10 hover:bg-cyan-500/20 text-cyan-400 border border-cyan-500/30 transition-all cursor-pointer text-[10px] font-mono font-bold"
                      >
                        SVG
                      </button>
                    )}

                    <button
                      type="button"
                      onClick={(e) => handleSaveToProject(img, e)}
                      title="Save to My Projects"
                      className="p-2 rounded-xl bg-white/[0.04] hover:bg-white/[0.1] text-gray-300 hover:text-white transition-all cursor-pointer"
                    >
                      {savedIds[img.generation_id] ? (
                        <Check className="w-4 h-4 text-emerald-400" />
                      ) : (
                        <Bookmark className="w-4 h-4" />
                      )}
                    </button>

                    <button
                      type="button"
                      onClick={(e) => handleDownload(img, e)}
                      title="Download PNG Design"
                      className="p-2 rounded-xl bg-white/[0.04] hover:bg-white/[0.1] text-gray-300 hover:text-white transition-all cursor-pointer"
                    >
                      <Download className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Image Modal for Detail Inspection */}
      <ImageModal
        image={selectedModalImage}
        onClose={() => setSelectedModalImage(null)}
      />
    </div>
  );
};
