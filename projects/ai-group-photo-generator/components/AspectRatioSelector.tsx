import React from 'react';

type AspectRatio = '1:1' | '9:16' | '16:9';
const RATIO_OPTIONS: AspectRatio[] = ['1:1', '9:16', '16:9'];

interface AspectRatioSelectorProps {
  selectedRatio: AspectRatio;
  onRatioChange: (ratio: AspectRatio) => void;
}

const AspectRatioSelector: React.FC<AspectRatioSelectorProps> = ({ selectedRatio, onRatioChange }) => {
  return (
    <div>
      <label className="block text-lg font-bold text-gray-900 mb-2">
        Aspect Ratio
      </label>
      <div className="grid grid-cols-3 gap-3">
        {RATIO_OPTIONS.map(ratio => (
          <button
            key={ratio}
            type="button"
            onClick={() => onRatioChange(ratio)}
            className={`px-4 py-3 text-sm font-semibold rounded-lg border-2 transition-all duration-200 flex items-center justify-center ${
              selectedRatio === ratio
                ? 'bg-indigo-600 border-indigo-600 text-white shadow-md'
                : 'bg-white border-gray-300 text-gray-700 hover:border-indigo-500 hover:text-indigo-600'
            }`}
          >
            {ratio}
          </button>
        ))}
      </div>
    </div>
  );
};

export default AspectRatioSelector;
