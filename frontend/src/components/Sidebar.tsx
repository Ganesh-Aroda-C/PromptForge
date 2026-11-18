import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  Compass,
  Wand2,
  FolderKanban,
  Settings,
  Layers
} from 'lucide-react';

export const Sidebar: React.FC = () => {
  const navItems = [
    { to: '/', label: 'Explore', icon: Compass },
    { to: '/create', label: 'Create', icon: Wand2, highlight: true },
    { to: '/projects', label: 'My Projects', icon: FolderKanban },
    { to: '/settings', label: 'Settings', icon: Settings },
  ];

  return (
    <aside className="w-64 h-screen fixed left-0 top-0 bg-[#0A0C10] border-r border-white/5 flex flex-col justify-between z-30 select-none">
      <div>
        {/* Brand Logo */}
        <div className="h-16 flex items-center px-6 gap-3 border-b border-white/5">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-cyan-500 to-blue-600 flex items-center justify-center shadow-lg shadow-cyan-500/20">
            <Layers className="w-5 h-5 text-white" />
          </div>
          <div>
            <span className="font-semibold text-base tracking-tight text-white flex items-center gap-1.5">
              PromptForge <span className="text-xs px-1.5 py-0.5 rounded bg-cyan-500/10 text-cyan-400 font-mono">AI</span>
            </span>
            <p className="text-[10px] text-gray-500 tracking-wider uppercase font-medium">Design Studio</p>
          </div>
        </div>

        {/* Clean Navigation Menu */}
        <nav className="p-4 space-y-1.5">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all duration-150 ${
                    isActive
                      ? 'bg-white/10 text-white shadow-sm font-semibold'
                      : 'text-gray-400 hover:text-gray-200 hover:bg-white/[0.04]'
                  } ${item.highlight ? 'text-cyan-400' : ''}`
                }
              >
                <Icon className={`w-4 h-4 ${item.highlight ? 'text-cyan-400' : ''}`} />
                <span>{item.label}</span>
                {item.highlight && (
                  <span className="ml-auto w-2 h-2 rounded-full bg-cyan-400 animate-pulse" />
                )}
              </NavLink>
            );
          })}
        </nav>
      </div>

      {/* Clean Bottom Footer */}
      <div className="p-4 border-t border-white/5">
        <div className="px-3 py-2 flex items-center justify-between text-xs text-gray-500">
          <span className="font-medium text-gray-400">PromptForge Studio</span>
          <span className="font-mono text-[10px]">v1.0</span>
        </div>
      </div>
    </aside>
  );
};
