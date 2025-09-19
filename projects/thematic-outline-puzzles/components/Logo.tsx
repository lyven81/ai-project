
import React from 'react';

export function Logo() {
  return (
    <svg 
      width="48" 
      height="48" 
      viewBox="0 0 24 24" 
      fill="none" 
      xmlns="http://www.w3.org/2000/svg"
      className="text-sky-500"
    >
      <path d="M10 4a2 2 0 10-4 0v2a2 2 0 104 0V4z" fill="currentColor"/>
      <path d="M18 4a2 2 0 10-4 0v2a2 2 0 104 0V4z" fill="currentColor" fillOpacity="0.8"/>
      <path d="M10 12a2 2 0 10-4 0v2a2 2 0 104 0v-2z" fill="currentColor" fillOpacity="0.6"/>
      <path d="M14 12h4a2 2 0 100-4h-2a2 2 0 100 4zm0 0v4a2 2 0 104 0v-2a2 2 0 10-4 0z" fill="currentColor"/>
      <path d="M6 16H4a2 2 0 100 4h2a2 2 0 100-4z" fill="currentColor" fillOpacity="0.4"/>
    </svg>
  );
}
