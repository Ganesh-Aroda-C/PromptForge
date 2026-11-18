import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, Plus } from 'lucide-react';

interface TopNavProps {
  searchQuery: string;
  onSearchChange: (q: string) => void;
}

export const TopNav: React.FC<TopNavProps> = ({ searchQuery, onSearchChange }) => {
  const navigate = useNavigate();

  return (
    <header className="h-16 pl-64 pr-8 bg-[#090A0C]/80 backdrop-blur-md border-b border-white/5 fixed top-0 right-0 left-0 z-20 flex items-center justify-between">
      {/* Search Input */}
      <div className="relative w-96 ml-6">
        <Search className="w-4 h-4 text-gray-500 absolute left-3.5 top-1/2 -translate-y-1/2" />
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => onSearchChange(e.target.value)}
          placeholder="Search designs, concepts, or styles..."
          className="w-full pl-10 pr-4 py-2 bg-white/[0.04] border border-white/10 rounded-xl text-sm text-gray-200 placeholder-gray-500 focus:outline-none focus:border-cyan-500/50 transition-colors"
        />
      </div>

      {/* Action Controls & Profile */}
      <div className="flex items-center gap-4">
        {/* Create Quick Button */}
        <button
          onClick={() => navigate('/create')}
          className="flex items-center gap-2 px-4 py-2 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 text-white text-xs font-semibold hover:opacity-95 shadow-lg shadow-cyan-500/20 transition-all cursor-pointer"
        >
          <Plus className="w-3.5 h-3.5" />
          <span>New Design</span>
        </button>

        {/* Profile Avatar */}
        <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-cyan-500 to-blue-600 flex items-center justify-center text-xs font-semibold text-white ring-2 ring-white/10 select-none">
          PF
        </div>
      </div>
    </header>
  );
};
