
import React from 'react';
import { AgeGroup, DrawingStyle } from '../types';
import { AGE_GROUPS, DRAWING_STYLES } from '../constants';
import { DownloadIcon, SparklesIcon } from './icons';

interface ControlsPanelProps {
  theme: string;
  setTheme: (theme: string) => void;
  ageGroup: AgeGroup;
  setAgeGroup: (ageGroup: AgeGroup) => void;
  style: DrawingStyle;
  setStyle: (style: DrawingStyle) => void;
  onGenerate: () => void;
  onDownload: () => void;
  isLoading: boolean;
  pagesGenerated: boolean;
}

const ControlsPanel: React.FC<ControlsPanelProps> = ({
  theme,
  setTheme,
  ageGroup,
  setAgeGroup,
  style,
  setStyle,
  onGenerate,
  onDownload,
  isLoading,
  pagesGenerated,
}) => {
  return (
    <div className="bg-white p-6 rounded-2xl shadow-lg border border-slate-200 sticky top-8">
      <h2 className="text-2xl font-bold text-slate-800 mb-6">Create Your Page</h2>
      <div className="space-y-6">
        <div>
          <label htmlFor="theme" className="block text-sm font-medium text-slate-600 mb-1">
            1. Enter a Theme
          </label>
          <input
            type="text"
            id="theme"
            value={theme}
            onChange={(e) => setTheme(e.target.value)}
            placeholder="e.g., Space adventure"
            className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition"
            disabled={isLoading || pagesGenerated}
          />
        </div>
        <div>
          <label htmlFor="age-group" className="block text-sm font-medium text-slate-600 mb-1">
            2. Select Age Group
          </label>
          <select
            id="age-group"
            value={ageGroup.label}
            onChange={(e) => setAgeGroup(AGE_GROUPS.find(ag => ag.label === e.target.value) || AGE_GROUPS[0])}
            className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition bg-white"
            disabled={isLoading || pagesGenerated}
          >
            {AGE_GROUPS.map(ag => <option key={ag.label}>{ag.label}</option>)}
          </select>
        </div>
        <div>
          <label htmlFor="style" className="block text-sm font-medium text-slate-600 mb-1">
            3. Choose Drawing Style
          </label>
          <select
            id="style"
            value={style.label}
            onChange={(e) => setStyle(DRAWING_STYLES.find(s => s.label === e.target.value) || DRAWING_STYLES[0])}
            className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition bg-white"
            disabled={isLoading || pagesGenerated}
          >
            {DRAWING_STYLES.map(s => <option key={s.label}>{s.label}</option>)}
          </select>
        </div>
      </div>
      <div className="mt-8 pt-6 border-t border-slate-200 space-y-4">
        <button
          onClick={onGenerate}
          disabled={isLoading || pagesGenerated}
          className="w-full flex items-center justify-center bg-indigo-600 text-white font-bold py-3 px-4 rounded-lg hover:bg-indigo-700 disabled:bg-indigo-300 disabled:cursor-not-allowed transition-all duration-300 transform hover:scale-105"
        >
          <SparklesIcon />
          <span className="ml-2">{isLoading ? 'Generating...' : 'Generate Page'}</span>
        </button>
        <button
          onClick={onDownload}
          disabled={!pagesGenerated || isLoading}
          className="w-full flex items-center justify-center bg-emerald-500 text-white font-bold py-3 px-4 rounded-lg hover:bg-emerald-600 disabled:bg-emerald-300 disabled:cursor-not-allowed transition-all duration-300 transform hover:scale-105"
        >
          <DownloadIcon />
          <span className="ml-2">{isLoading ? 'Downloading...' : 'Download as PDF'}</span>
        </button>
      </div>
    </div>
  );
};

export default ControlsPanel;
