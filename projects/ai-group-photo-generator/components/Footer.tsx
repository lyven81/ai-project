import React from 'react';

const Footer: React.FC = () => {
  return (
    <footer className="bg-white mt-12">
      <div className="container mx-auto py-6 px-4 text-center text-gray-500">
        <p>&copy; {new Date().getFullYear()} AI Group Photo Generator. All rights reserved.</p>
        <p className="text-sm mt-1">Powered by Google Gemini</p>
      </div>
    </footer>
  );
};

export default Footer;
