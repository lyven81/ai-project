import React from 'react';
import { Theme } from '../types';
import { THEME_OPTIONS } from '../constants';

interface ThemeSelectorProps {
  selectedTheme: Theme;
  onThemeChange: (theme: Theme) => void;
}

const ThemeSelector: React.FC<ThemeSelectorProps> = ({ selectedTheme, onThemeChange }) => {
  return (
    <div>
      <label htmlFor="theme" className="block text-lg font-bold text-gray-900 mb-2">
        Select a Theme
      </label>
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {THEME_OPTIONS.map(theme => (
          <button
            key={theme}
            type="button"
            onClick={() => onThemeChange(theme)}
            className={`px-4 py-3 text-sm font-semibold rounded-lg border-2 transition-all duration-200 ${
              selectedTheme === theme
                ? 'bg-indigo-600 border-indigo-600 text-white shadow-md'
                : 'bg-white border-gray-300 text-gray-700 hover:border-indigo-500 hover:text-indigo-600'
            }`}
          >
            {theme}
          </button>
        ))}
      </div>
    </div>
  );
};

export default ThemeSelector;
