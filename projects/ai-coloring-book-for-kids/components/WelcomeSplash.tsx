
import React from 'react';

export const WelcomeSplash: React.FC = () => {
  return (
    <div className="text-center p-8">
      <div className="text-6xl mb-4">🎨</div>
      <h2 className="text-2xl font-bold text-gray-700">Let's Get Coloring!</h2>
      <p className="text-gray-500 mt-2">
        Type a theme like "friendly monsters" or "race cars" into the box,
        <br />
        then click <strong>Generate</strong> to start the fun!
      </p>
    </div>
  );
};
