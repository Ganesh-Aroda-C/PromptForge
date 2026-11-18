import React, { useState, useEffect } from 'react';
import {
  Database,
  Download,
  Plus,
  Trash2,
  Search,
  FileSpreadsheet,
  FileCode,
  ShieldCheck,
  Tag
} from 'lucide-react';
import { api } from '../services/api';
import { Dataset, DatasetRecord } from '../types';

export const DatasetStudioPage: React.FC = () => {
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [selectedDataset, setSelectedDataset] = useState<Dataset | null>(null);
  const [searchRecord, setSearchRecord] = useState('');
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);

  // New Record Form State
  const [recInputPrompt, setRecInputPrompt] = useState('');
  const [recOptimizedPrompt, setRecOptimizedPrompt] = useState('');
  const [recNegativePrompt, setRecNegativePrompt] = useState('');
  const [recCategory, setRecCategory] = useState('electric_motorcycle');

  useEffect(() => {
    loadDatasets();
  }, []);

  const loadDatasets = async () => {
    try {
      setLoading(true);
      const data = await api.listDatasets();
      setDatasets(data);
      if (data.length > 0) {
        // Load details of the first dataset
        const full = await api.getDataset(data[0].dataset_id);
        setSelectedDataset(full);
      }
    } catch (err) {
      console.error('Failed to load datasets', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectDataset = async (datasetId: string) => {
    try {
      const full = await api.getDataset(datasetId);
      setSelectedDataset(full);
    } catch (err) {
      console.error('Failed to get dataset detail', err);
    }
  };

  const handleAddRecord = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedDataset || !recInputPrompt.trim()) return;

    const newRec: DatasetRecord = {
      record_id: `REC-${Date.now().toString().slice(-4)}`,
      task_type: 'industrial_product_design',
      product_category: recCategory,
      input_prompt: recInputPrompt,
      optimized_prompt: recOptimizedPrompt || recInputPrompt,
      negative_prompt: recNegativePrompt,
      objects: [recCategory],
      attributes: { category: recCategory },
      style: 'photorealistic 3d render',
      expected_constraints: [],
      evaluation_metadata: { source: 'custom_curation' }
    };

    try {
      await api.addDatasetRecord(selectedDataset.dataset_id, newRec);
      setShowAddModal(false);
      setRecInputPrompt('');
      setRecOptimizedPrompt('');
      setRecNegativePrompt('');
      handleSelectDataset(selectedDataset.dataset_id);
    } catch (err) {
      console.error('Failed to add record', err);
    }
  };

  const handleDeleteRecord = async (recordId: string) => {
    if (!selectedDataset) return;
    try {
      await api.deleteDatasetRecord(selectedDataset.dataset_id, recordId);
      handleSelectDataset(selectedDataset.dataset_id);
    } catch (err) {
      console.error('Failed to delete record', err);
    }
  };

  const handleExport = (format: 'json' | 'csv') => {
    if (!selectedDataset) return;
    window.open(`/api/datasets/${selectedDataset.dataset_id}/export?format=${format}`, '_blank');
  };

  const records = selectedDataset?.records || [];
  const filteredRecords = records.filter(
    (r) =>
      !searchRecord ||
      r.input_prompt.toLowerCase().includes(searchRecord.toLowerCase()) ||
      r.optimized_prompt.toLowerCase().includes(searchRecord.toLowerCase()) ||
      r.product_category.toLowerCase().includes(searchRecord.toLowerCase())
  );

  return (
    <div className="space-y-8 animate-fadeIn max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-white/5 pb-6">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2.5">
            <Database className="w-6 h-6 text-cyan-400" />
            <span>Dataset Studio & Benchmark Hub</span>
          </h1>
          <p className="text-xs text-gray-400 mt-1">
            Explore, validate, and curate prompt-image benchmarks (V-LAB, IDD, and DrawBench subsets).
          </p>
        </div>

        {selectedDataset && (
          <div className="flex items-center gap-2">
            <button
              onClick={() => handleExport('json')}
              className="px-3 py-1.5 rounded-xl bg-white/[0.04] hover:bg-white/[0.08] text-gray-300 text-xs font-mono flex items-center gap-1.5 border border-white/5 transition-colors"
            >
              <FileCode className="w-3.5 h-3.5 text-cyan-400" />
              <span>Export JSON</span>
            </button>
            <button
              onClick={() => handleExport('csv')}
              className="px-3 py-1.5 rounded-xl bg-white/[0.04] hover:bg-white/[0.08] text-gray-300 text-xs font-mono flex items-center gap-1.5 border border-white/5 transition-colors"
            >
              <FileSpreadsheet className="w-3.5 h-3.5 text-emerald-400" />
              <span>Export CSV</span>
            </button>
          </div>
        )}
      </div>

      {/* Dataset Selection Tabs */}
      <div className="flex items-center gap-3 overflow-x-auto pb-2">
        {datasets.map((ds) => (
          <button
            key={ds.dataset_id}
            onClick={() => handleSelectDataset(ds.dataset_id)}
            className={`px-4 py-2.5 rounded-xl text-xs font-medium text-left transition-all border whitespace-nowrap ${
              selectedDataset?.dataset_id === ds.dataset_id
                ? 'bg-cyan-500/15 border-cyan-500/40 text-cyan-300 font-semibold shadow-md'
                : 'bg-white/[0.02] border-white/5 text-gray-400 hover:text-white hover:bg-white/[0.05]'
            }`}
          >
            <div className="flex items-center gap-2">
              <span>{ds.name}</span>
              <span className="px-1.5 py-0.2 rounded bg-white/10 text-[10px] font-mono">
                {ds.record_count}
              </span>
            </div>
          </button>
        ))}
      </div>

      {/* Selected Dataset Details & Records Table */}
      {selectedDataset && (
        <div className="space-y-6">
          {/* Dataset Info Banner */}
          <div className="surface-card p-5 rounded-2xl flex flex-col sm:flex-row sm:items-center justify-between gap-4 border border-white/5">
            <div>
              <div className="flex items-center gap-2">
                <span className="text-sm font-bold text-white">{selectedDataset.name}</span>
                <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-cyan-500/10 text-cyan-400">
                  {selectedDataset.source}
                </span>
              </div>
              <p className="text-xs text-gray-400 mt-1 max-w-2xl">{selectedDataset.description}</p>
            </div>

            <button
              onClick={() => setShowAddModal(true)}
              className="px-4 py-2 rounded-xl bg-cyan-500 text-black text-xs font-semibold hover:bg-cyan-400 transition-colors flex items-center gap-1.5 self-start sm:self-auto"
            >
              <Plus className="w-3.5 h-3.5" />
              <span>Add Record</span>
            </button>
          </div>

          {/* Search bar */}
          <div className="relative">
            <Search className="w-4 h-4 text-gray-500 absolute left-3.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={searchRecord}
              onChange={(e) => setSearchRecord(e.target.value)}
              placeholder="Filter benchmark records by prompt or category..."
              className="w-full pl-10 pr-4 py-2.5 bg-white/[0.02] border border-white/10 rounded-xl text-xs text-gray-200 placeholder-gray-500 focus:outline-none focus:border-cyan-500/50"
            />
          </div>

          {/* Records Table */}
          <div className="surface-card rounded-2xl overflow-hidden border border-white/5">
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-white/[0.03] text-gray-400 font-mono text-[11px] uppercase tracking-wider border-b border-white/5">
                  <tr>
                    <th className="py-3 px-4">ID</th>
                    <th className="py-3 px-4">Domain</th>
                    <th className="py-3 px-4">Input Prompt</th>
                    <th className="py-3 px-4">Optimized Progressive Prompt</th>
                    <th className="py-3 px-4">Negative Constraints</th>
                    <th className="py-3 px-4 text-right">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-white/5 font-mono text-[11px]">
                  {filteredRecords.map((r) => (
                    <tr key={r.record_id} className="hover:bg-white/[0.02] transition-colors">
                      <td className="py-3 px-4 text-cyan-400 font-bold whitespace-nowrap">{r.record_id}</td>
                      <td className="py-3 px-4 whitespace-nowrap text-gray-400 capitalize">
                        {r.product_category.replace('_', ' ')}
                      </td>
                      <td className="py-3 px-4 text-gray-300 max-w-xs truncate">{r.input_prompt}</td>
                      <td className="py-3 px-4 text-cyan-200 max-w-sm truncate">{r.optimized_prompt}</td>
                      <td className="py-3 px-4 text-gray-500 max-w-xs truncate">{r.negative_prompt || '—'}</td>
                      <td className="py-3 px-4 text-right">
                        <button
                          onClick={() => handleDeleteRecord(r.record_id)}
                          className="p-1 rounded text-gray-500 hover:text-rose-400 transition-colors"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* Add Record Modal */}
      {showAddModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-fadeIn">
          <div className="w-full max-w-lg surface-card p-6 rounded-2xl border border-white/10 space-y-4 shadow-2xl">
            <h3 className="text-base font-bold text-white">Add Dataset Benchmark Record</h3>
            <form onSubmit={handleAddRecord} className="space-y-4 text-xs">
              <div>
                <label className="text-gray-300 block mb-1">Product Category</label>
                <select
                  value={recCategory}
                  onChange={(e) => setRecCategory(e.target.value)}
                  className="w-full bg-white/[0.04] border border-white/10 rounded-xl p-2.5 text-white"
                >
                  <option value="electric_motorcycle">Electric Motorcycle</option>
                  <option value="electric_vehicle">Electric Vehicle</option>
                  <option value="consumer_electronics">Consumer Electronics</option>
                  <option value="furniture">Furniture</option>
                  <option value="smart_device">Smart Device</option>
                </select>
              </div>

              <div>
                <label className="text-gray-300 block mb-1">Baseline Input Prompt</label>
                <textarea
                  rows={2}
                  required
                  value={recInputPrompt}
                  onChange={(e) => setRecInputPrompt(e.target.value)}
                  placeholder="e.g., minimalist electric scooter concept"
                  className="w-full bg-white/[0.04] border border-white/10 rounded-xl p-2.5 text-white"
                />
              </div>

              <div>
                <label className="text-gray-300 block mb-1">Optimized Prompt (Optional)</label>
                <textarea
                  rows={3}
                  value={recOptimizedPrompt}
                  onChange={(e) => setRecOptimizedPrompt(e.target.value)}
                  placeholder="Full staged prompt..."
                  className="w-full bg-white/[0.04] border border-white/10 rounded-xl p-2.5 text-white"
                />
              </div>

              <div className="flex items-center justify-end gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="px-4 py-2 rounded-xl text-gray-400 hover:text-white"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-5 py-2.5 rounded-xl bg-cyan-500 text-black font-semibold hover:bg-cyan-400 transition-colors"
                >
                  Save Record
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
