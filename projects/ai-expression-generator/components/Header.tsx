import React from 'react';

const Header: React.FC = () => {
  return (
    <header className="text-center">
      <h1 className="text-4xl sm:text-5xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-indigo-600">
        AI Expression Generator
      </h1>
      <p className="mt-4 text-lg text-gray-400 max-w-2xl mx-auto">
        Upload a photo to see yourself with nine different AI-generated facial expressions. Discover your acting range!
      </p>
    </header>
  );
};

export default Header;
