import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  FolderKanban,
  Plus,
  Trash2,
  Calendar,
  Layers,
  Wand2,
  ArrowRight,
  ExternalLink
} from 'lucide-react';
import { api } from '../services/api';
import { Project } from '../types';

export const ProjectsPage: React.FC = () => {
  const navigate = useNavigate();
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newTitle, setNewTitle] = useState('');
  const [newDesc, setNewDesc] = useState('');
  const [newCategory, setNewCategory] = useState('industrial_design');

  useEffect(() => {
    loadProjects();
  }, []);

  const loadProjects = async () => {
    try {
      setLoading(true);
      const data = await api.listProjects();
      setProjects(data);
    } catch (err) {
      console.error('Failed to load projects', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateProject = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTitle.trim()) return;
    try {
      await api.createProject({
        title: newTitle,
        description: newDesc,
        category: newCategory,
        tags: [newCategory, 'research']
      });
      setShowCreateModal(false);
      setNewTitle('');
      setNewDesc('');
      loadProjects();
    } catch (err) {
      console.error('Failed to create project', err);
    }
  };

  const handleDelete = async (projectId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (window.confirm('Are you sure you want to delete this project?')) {
      try {
        await api.deleteProject(projectId);
        loadProjects();
      } catch (err) {
        console.error('Failed to delete project', err);
      }
    }
  };

  return (
    <div className="space-y-8 animate-fadeIn max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-white/5 pb-6">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2.5">
            <FolderKanban className="w-6 h-6 text-cyan-400" />
            <span>My Design Projects</span>
          </h1>
          <p className="text-xs text-gray-400 mt-1">
            Persisted industrial design concepts, prompt version lineages, and visual prototyping logs.
          </p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="px-4 py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 text-white text-xs font-semibold hover:opacity-95 shadow-lg shadow-cyan-500/20 flex items-center gap-2 transition-all"
        >
          <Plus className="w-4 h-4" />
          <span>New Project</span>
        </button>
      </div>

      {/* Projects Grid */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3].map((n) => (
            <div key={n} className="h-56 surface-card rounded-2xl animate-pulse" />
          ))}
        </div>
      ) : projects.length === 0 ? (
        <div className="py-20 text-center space-y-4 surface-card rounded-2xl border-dashed border-white/10 p-8">
          <FolderKanban className="w-10 h-10 text-gray-500 mx-auto" />
          <p className="text-sm text-gray-400">No design projects created yet.</p>
          <button
            onClick={() => setShowCreateModal(true)}
            className="px-4 py-2 rounded-xl bg-white/[0.05] hover:bg-white/10 text-cyan-400 text-xs font-medium border border-white/5 transition-colors"
          >
            Create Your First Project
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {projects.map((proj) => (
            <div
              key={proj.project_id}
              onClick={() => navigate('/create')}
              className="surface-card group rounded-2xl overflow-hidden cursor-pointer border border-white/5 hover:border-cyan-500/30 transition-all flex flex-col justify-between"
            >
              {/* Thumbnail Header */}
              <div className="h-40 bg-black/40 overflow-hidden relative">
                {proj.thumbnail_url ? (
                  <img
                    src={proj.thumbnail_url}
                    alt={proj.title}
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                  />
                ) : (
                  <div className="w-full h-full flex items-center justify-center bg-gradient-to-br from-[#121419] to-[#0A0C10] text-gray-600">
                    <Layers className="w-8 h-8 opacity-40" />
                  </div>
                )}
                <div className="absolute top-3 right-3">
                  <button
                    onClick={(e) => handleDelete(proj.project_id, e)}
                    className="p-1.5 rounded-lg bg-black/60 text-gray-400 hover:text-rose-400 transition-colors"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
                <div className="absolute bottom-3 left-3">
                  <span className="px-2.5 py-0.5 rounded-lg bg-black/70 backdrop-blur-sm text-[10px] font-mono text-cyan-300 border border-white/10 capitalize">
                    {proj.category.replace('_', ' ')}
                  </span>
                </div>
              </div>

              {/* Body */}
              <div className="p-5 space-y-3 flex-1 flex flex-col justify-between">
                <div>
                  <h3 className="text-base font-semibold text-white group-hover:text-cyan-400 transition-colors">
                    {proj.title}
                  </h3>
                  <p className="text-xs text-gray-400 mt-1 line-clamp-2 leading-relaxed">
                    {proj.description || 'No description provided.'}
                  </p>
                </div>

                <div className="pt-3 border-t border-white/5 flex items-center justify-between text-xs text-gray-500 font-mono">
                  <span>{proj.generations_count} Concepts</span>
                  <span className="flex items-center gap-1 text-cyan-400 group-hover:translate-x-0.5 transition-transform">
                    Open <ArrowRight className="w-3.5 h-3.5" />
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Create Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-fadeIn">
          <div className="w-full max-w-md surface-card p-6 rounded-2xl border border-white/10 space-y-4 shadow-2xl">
            <h3 className="text-base font-bold text-white">Create New Project</h3>
            <form onSubmit={handleCreateProject} className="space-y-4 text-xs">
              <div>
                <label className="text-gray-300 block mb-1">Project Title</label>
                <input
                  type="text"
                  required
                  value={newTitle}
                  onChange={(e) => setNewTitle(e.target.value)}
                  placeholder="e.g., AeroStrata Electric Superbike"
                  className="w-full bg-white/[0.04] border border-white/10 rounded-xl p-3 text-white focus:outline-none focus:border-cyan-500/50"
                />
              </div>

              <div>
                <label className="text-gray-300 block mb-1">Design Category</label>
                <select
                  value={newCategory}
                  onChange={(e) => setNewCategory(e.target.value)}
                  className="w-full bg-white/[0.04] border border-white/10 rounded-xl p-3 text-white focus:outline-none focus:border-cyan-500/50"
                >
                  <option value="electric_motorcycle">Electric Motorcycle</option>
                  <option value="electric_vehicle">Electric Vehicle</option>
                  <option value="consumer_electronics">Consumer Electronics</option>
                  <option value="smart_device">Smart Device</option>
                  <option value="furniture">Furniture</option>
                  <option value="industrial_equipment">Industrial Equipment</option>
                  <option value="architectural_concept">Architectural Concept</option>
                </select>
              </div>

              <div>
                <label className="text-gray-300 block mb-1">Project Description</label>
                <textarea
                  rows={3}
                  value={newDesc}
                  onChange={(e) => setNewDesc(e.target.value)}
                  placeholder="Project goals, target materials, and specifications..."
                  className="w-full bg-white/[0.04] border border-white/10 rounded-xl p-3 text-white focus:outline-none focus:border-cyan-500/50 resize-none"
                />
              </div>

              <div className="flex items-center justify-end gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="px-4 py-2 rounded-xl text-gray-400 hover:text-white"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-5 py-2.5 rounded-xl bg-cyan-500 text-black font-semibold hover:bg-cyan-400 transition-colors"
                >
                  Create
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
