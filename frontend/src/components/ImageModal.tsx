import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { X, Copy, Wand2, CheckCircle2, Download, Check, Bookmark, Sparkles } from 'lucide-react';
import { GeneratedImage } from '../types';
import { api } from '../services/api';

interface ImageModalProps {
  image: GeneratedImage | null;
  onClose: () => void;
}

export const ImageModal: React.FC<ImageModalProps> = ({ image, onClose }) => {
  const navigate = useNavigate();
  const [copied, setCopied] = useState(false);
  const [saved, setSaved] = useState(false);

  if (!image) return null;

  const handleCopy = () => {
    navigator.clipboard.writeText(image.prompt);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = async () => {
    try {
      const response = await fetch(image.image_url);
      const blob = await response.blob();
      const blobUrl = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = blobUrl;
      link.download = `PromptForge-${image.generation_id}.png`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(blobUrl);
    } catch (err) {
      window.open(image.image_url, '_blank');
    }
  };

  const handleDownloadSvg = () => {
    const svgUrl = image.image_url.replace(/\.png$/, '.svg');
    const link = document.createElement('a');
    link.href = svgUrl;
    link.download = `PromptForge-${image.generation_id}.svg`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const handleSave = async () => {
    setSaved(true);
    try {
      await api.createProject({
        title: (image.prompt.length > 45 ? image.prompt.slice(0, 42) + '...' : image.prompt),
        description: `Saved design concept. Prompt: ${image.prompt}`,
        category: 'design',
        tags: ['saved-design']
      });
    } catch (e) {
      console.warn(e);
    }
    setTimeout(() => setSaved(false), 2000);
  };

  const handleRefine = () => {
    onClose();
    navigate('/create', { state: { initialPrompt: image.prompt, negativePrompt: image.negative_prompt } });
  };

  const handleEvaluate = () => {
    onClose();
    navigate('/evaluation', { state: { selectedImage: image } });
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/85 backdrop-blur-md animate-fadeIn">
      <div className="relative w-full max-w-5xl max-h-[90vh] bg-[#111215] border border-white/10 rounded-3xl overflow-hidden shadow-2xl flex flex-col md:flex-row">
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 z-10 p-2 rounded-full bg-black/60 text-gray-300 hover:text-white hover:bg-black/80 transition-colors"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Visual Preview Side */}
        <div className="md:w-3/5 bg-black/60 flex items-center justify-center p-6 border-b md:border-b-0 md:border-r border-white/5">
          <img
            src={image.image_url}
            alt={image.prompt}
            className="max-h-[75vh] w-auto max-w-full rounded-2xl object-contain shadow-2xl"
          />
        </div>

        {/* Details & Actions Side */}
        <div className="md:w-2/5 p-6 flex flex-col justify-between overflow-y-auto">
          <div className="space-y-5">
            {/* Header info */}
            <div>
              <div className="flex items-center gap-2 mb-2">
                <span className="px-2.5 py-0.5 rounded-full text-[11px] font-mono bg-cyan-500/10 text-cyan-400">
                  Concept Design
                </span>
                <span className="px-2.5 py-0.5 rounded-full text-[11px] font-mono bg-white/5 text-gray-300">
                  High Resolution
                </span>
              </div>
              <h3 className="text-lg font-bold text-white leading-snug">Design Preview</h3>
            </div>

            {/* Prompt Section */}
            <div className="space-y-1.5">
              <div className="flex items-center justify-between text-xs text-gray-400">
                <span className="font-medium">Prompt Specification</span>
                <button
                  onClick={handleCopy}
                  className="flex items-center gap-1 text-cyan-400 hover:text-cyan-300 transition-colors"
                >
                  {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                  <span>{copied ? 'Copied' : 'Copy'}</span>
                </button>
              </div>
              <p className="text-xs text-gray-200 bg-white/[0.03] p-3 rounded-2xl border border-white/5 leading-relaxed font-mono select-text">
                {image.prompt}
              </p>
            </div>

            {/* Technical Parameters */}
            <div className="grid grid-cols-2 gap-2 text-[11px] font-mono text-gray-400 bg-white/[0.02] p-3 rounded-2xl border border-white/5">
              <div>
                <span className="text-gray-500 block">Seed</span>
                <span className="text-gray-200">{image.seed}</span>
              </div>
              <div>
                <span className="text-gray-500 block">Dimensions</span>
                <span className="text-gray-200">{image.width} × {image.height}</span>
              </div>
              <div>
                <span className="text-gray-500 block">Status</span>
                <span className="text-emerald-400">Render Complete</span>
              </div>
              <div>
                <span className="text-gray-500 block">Concept ID</span>
                <span className="text-gray-200 truncate">{image.generation_id}</span>
              </div>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="pt-6 space-y-2.5 border-t border-white/5">
            <div className="flex items-center gap-2">
              <button
                onClick={handleDownload}
                className="flex-1 flex items-center justify-center gap-2 py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 text-white font-medium text-xs shadow-lg shadow-cyan-500/20 hover:opacity-95 transition-all"
              >
                <Download className="w-4 h-4" />
                <span>Download PNG</span>
              </button>

              {image.image_url.includes('vector_') && (
                <button
                  onClick={handleDownloadSvg}
                  className="py-2.5 px-3 rounded-xl bg-white/[0.06] hover:bg-white/[0.12] text-cyan-300 font-medium text-xs transition-colors border border-cyan-500/30 flex items-center gap-1.5"
                  title="Download Scalable Vector Graphics"
                >
                  <Download className="w-3.5 h-3.5" />
                  <span>SVG</span>
                </button>
              )}

              <button
                onClick={handleSave}
                className={`py-2.5 px-4 rounded-xl text-xs font-medium flex items-center justify-center gap-1.5 transition-colors border ${
                  saved
                    ? 'bg-emerald-500/20 text-emerald-400 border-emerald-500/40'
                    : 'bg-white/[0.05] hover:bg-white/[0.1] text-gray-200 border-white/10'
                }`}
              >
                {saved ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Bookmark className="w-3.5 h-3.5" />}
                <span>{saved ? 'Saved' : 'Save'}</span>
              </button>
            </div>

            <div className="flex items-center gap-2">
              <button
                onClick={handleRefine}
                className="flex-1 flex items-center justify-center gap-2 py-2 rounded-xl bg-white/[0.03] hover:bg-white/[0.08] text-gray-300 font-medium text-xs transition-colors border border-white/5"
              >
                <Wand2 className="w-3.5 h-3.5" />
                <span>Remix in Create</span>
              </button>

              <button
                onClick={handleEvaluate}
                className="flex-1 flex items-center justify-center gap-2 py-2 rounded-xl bg-white/[0.03] hover:bg-white/[0.08] text-gray-300 font-medium text-xs transition-colors border border-white/5"
              >
                <CheckCircle2 className="w-3.5 h-3.5 text-cyan-400" />
                <span>Quality Inspection</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
