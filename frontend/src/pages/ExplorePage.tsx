import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Sparkles, Wand2, ArrowUpRight, Filter, Eye } from 'lucide-react';
import { api } from '../services/api';
import { GeneratedImage } from '../types';
import { ImageModal } from '../components/ImageModal';

const CATEGORIES = [
  { id: 'all', label: 'All Designs' },
  { id: 'electric_motorcycle', label: 'Electric Motorcycles' },
  { id: 'electric_vehicle', label: 'Electric Vehicles' },
  { id: 'consumer_electronics', label: 'Electronics & Audio' },
  { id: 'smart_device', label: 'Smart Devices' },
  { id: 'furniture', label: 'Furniture' },
  { id: 'architectural_concept', label: 'Architecture' },
];

export const ExplorePage: React.FC<{ searchQuery: string }> = ({ searchQuery }) => {
  const navigate = useNavigate();
  const [images, setImages] = useState<GeneratedImage[]>([]);
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [selectedImage, setSelectedImage] = useState<GeneratedImage | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadGallery();
  }, []);

  const loadGallery = async () => {
    try {
      setLoading(true);
      const data = await api.listGenerations();
      // If empty, trigger a sample generation so the user always sees stunning real concepts
      if (!data || data.length === 0) {
        const seedRes = await api.generateImages({
          prompt: "high-end minimalist electric urban motorcycle with carbon fiber frame and LED lighting",
          num_images: 4
        });
        setImages(seedRes.generations);
      } else {
        setImages(data);
      }
    } catch (err) {
      console.error('Failed to load gallery', err);
    } finally {
      setLoading(false);
    }
  };

  const filteredImages = images.filter((img) => {
    const matchesCategory =
      selectedCategory === 'all' ||
      img.prompt.toLowerCase().includes(selectedCategory.replace('_', ' ')) ||
      (selectedCategory === 'consumer_electronics' && (img.prompt.includes('headphone') || img.prompt.includes('watch') || img.prompt.includes('audio')));
    
    const matchesSearch =
      !searchQuery ||
      img.prompt.toLowerCase().includes(searchQuery.toLowerCase()) ||
      img.model_name.toLowerCase().includes(searchQuery.toLowerCase());

    return matchesCategory && matchesSearch;
  });

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Hero Discovery Banner */}
      <div className="relative rounded-3xl overflow-hidden p-8 sm:p-10 bg-gradient-to-br from-[#12141A] to-[#0D0F14] border border-white/5 shadow-2xl">
        <div className="absolute top-0 right-0 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="relative z-10 max-w-2xl space-y-4">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-cyan-500/10 border border-cyan-500/20 text-xs font-mono text-cyan-400">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Autonomous Design Synthesis & Generative CAD</span>
          </div>
          <h1 className="text-3xl sm:text-4xl font-bold tracking-tight text-white leading-tight">
            Synthesize Industrial Concepts with Engineering Precision
          </h1>
          <p className="text-sm text-gray-400 leading-relaxed">
            Transform ideas and specifications into production-ready 3D visual prototypes with automated prompt optimization, fine-grained material control, and visual fidelity inspection.
          </p>
          <div className="pt-2 flex items-center gap-3">
            <button
              onClick={() => navigate('/create')}
              className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 text-white text-sm font-medium hover:opacity-95 shadow-lg shadow-cyan-500/25 flex items-center gap-2 transition-all cursor-pointer"
            >
              <Wand2 className="w-4 h-4" />
              <span>Start Creating</span>
            </button>
            <button
              onClick={() => navigate('/prompt-lab')}
              className="px-4 py-2.5 rounded-xl bg-white/[0.04] hover:bg-white/[0.08] text-gray-300 text-sm font-medium border border-white/10 transition-colors cursor-pointer"
            >
              <span>Explore Lab</span>
            </button>
          </div>
        </div>
      </div>

      {/* Category Filter Chips */}
      <div className="flex items-center gap-2 overflow-x-auto pb-2 scrollbar-none">
        {CATEGORIES.map((cat) => (
          <button
            key={cat.id}
            onClick={() => setSelectedCategory(cat.id)}
            className={`px-4 py-2 rounded-xl text-xs font-medium whitespace-nowrap transition-all ${
              selectedCategory === cat.id
                ? 'bg-white text-black font-semibold shadow-md'
                : 'bg-white/[0.04] text-gray-400 hover:text-white hover:bg-white/[0.08] border border-white/5'
            }`}
          >
            {cat.label}
          </button>
        ))}
      </div>

      {/* Masonry Gallery Grid */}
      {loading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6">
          {[1, 2, 3, 4, 5, 6].map((n) => (
            <div key={n} className="h-80 rounded-2xl bg-white/[0.03] animate-pulse border border-white/5" />
          ))}
        </div>
      ) : filteredImages.length === 0 ? (
        <div className="py-20 text-center space-y-3">
          <p className="text-gray-400 text-sm">No concept designs found matching your filter criteria.</p>
          <button
            onClick={() => setSelectedCategory('all')}
            className="text-xs text-cyan-400 hover:underline"
          >
            Reset Filters
          </button>
        </div>
      ) : (
        <div className="masonry-grid">
          {filteredImages.map((img) => (
            <div
              key={img.generation_id}
              onClick={() => setSelectedImage(img)}
              className="masonry-item surface-card group rounded-2xl overflow-hidden cursor-pointer relative shadow-lg"
            >
              {/* Image Preview */}
              <div className="relative overflow-hidden bg-black/40">
                <img
                  src={img.image_url}
                  alt={img.prompt}
                  className="w-full h-auto object-cover transition-transform duration-500 group-hover:scale-[1.03]"
                  loading="lazy"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity flex flex-col justify-end p-4">
                  <p className="text-xs text-white line-clamp-2 font-mono">
                    {img.prompt}
                  </p>
                  <div className="mt-2 flex items-center justify-between text-[11px] text-gray-300">
                    <span>Seed: {img.seed}</span>
                    <span className="flex items-center gap-1 text-cyan-400 font-medium">
                      Inspect <ArrowUpRight className="w-3.5 h-3.5" />
                    </span>
                  </div>
                </div>
              </div>

              {/* Bottom Card Summary */}
              <div className="p-3.5 flex items-center justify-between border-t border-white/5 bg-[#0F1014]">
                <div className="truncate max-w-[190px]">
                  <p className="text-xs text-gray-200 font-medium truncate">{img.prompt}</p>
                  <p className="text-[10px] text-gray-500 font-mono">{img.model_name || 'SDXL + ControlNet'}</p>
                </div>
                {img.clip_score && (
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-cyan-500/10 text-cyan-400 font-medium">
                    {img.clip_score}
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Image Inspection Modal */}
      <ImageModal image={selectedImage} onClose={() => setSelectedImage(null)} />
    </div>
  );
};
