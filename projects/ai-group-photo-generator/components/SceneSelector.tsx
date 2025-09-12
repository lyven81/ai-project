import React from 'react';

interface SceneSelectorProps {
  scene: string;
  onSceneChange: (scene: string) => void;
}

const SceneSelector: React.FC<SceneSelectorProps> = ({ scene, onSceneChange }) => {
  return (
    <div>
      <label htmlFor="scene" className="block text-lg font-bold text-gray-900 mb-2">
        Describe the Scene <span className="font-normal text-gray-500">(Optional)</span>
      </label>
      <input
        id="scene"
        type="text"
        value={scene}
        onChange={(e) => onSceneChange(e.target.value)}
        placeholder="e.g., rooftop bar at sunset, modern office"
        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-colors"
      />
      <p className="mt-1 text-sm text-gray-500">Describe a background or leave blank for a neutral one.</p>
    </div>
  );
};

export default SceneSelector;