import React, { useState } from 'react';

interface DemoModeProps {
  projectName: string;
}

const DemoMode: React.FC<DemoModeProps> = ({ projectName }) => {
  const [showDemoResults, setShowDemoResults] = useState(false);

  const demoData = {
    'AI Photo Editor': {
      features: ['AI Enhancement', 'Filters', 'Brightness/Contrast', 'Export Options'],
      sampleResults: [
        'Enhanced photo with improved lighting',
        'Applied vintage filter with 85% opacity',
        'Adjusted contrast by +20% and brightness by +15%',
        'Exported as high-quality PNG (1920x1080)'
      ]
    }
  };

  const currentDemo = demoData[projectName as keyof typeof demoData] || demoData['AI Photo Editor'];

  return (
    <div className="demo-mode-container" style={{
      padding: '2rem',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      borderRadius: '12px',
      color: 'white',
      textAlign: 'center',
      maxWidth: '800px',
      margin: '2rem auto'
    }}>
      <div style={{ marginBottom: '1.5rem' }}>
        <h2>🎬 Demo Mode</h2>
        <p>Experience {projectName} without API keys!</p>
      </div>

      <div style={{
        background: 'rgba(255, 255, 255, 0.1)',
        borderRadius: '8px',
        padding: '1.5rem',
        marginBottom: '1.5rem'
      }}>
        <h3>✨ Available Features:</h3>
        <div style={{ display: 'flex', flexWrap: 'wrap', justifyContent: 'center', gap: '0.5rem', marginTop: '1rem' }}>
          {currentDemo.features.map((feature, index) => (
            <span key={index} style={{
              background: 'rgba(255, 255, 255, 0.2)',
              padding: '0.5rem 1rem',
              borderRadius: '20px',
              fontSize: '0.9rem'
            }}>
              {feature}
            </span>
          ))}
        </div>
      </div>

      <button
        onClick={() => setShowDemoResults(!showDemoResults)}
        style={{
          background: '#ff6b6b',
          color: 'white',
          border: 'none',
          padding: '1rem 2rem',
          borderRadius: '25px',
          fontSize: '1.1rem',
          cursor: 'pointer',
          transition: 'all 0.3s ease'
        }}
        onMouseOver={(e) => e.currentTarget.style.transform = 'scale(1.05)'}
        onMouseOut={(e) => e.currentTarget.style.transform = 'scale(1)'}
      >
        {showDemoResults ? 'Hide Demo Results' : 'Try Demo Features'}
      </button>

      {showDemoResults && (
        <div style={{
          background: 'rgba(255, 255, 255, 0.1)',
          borderRadius: '8px',
          padding: '1.5rem',
          marginTop: '1.5rem',
          textAlign: 'left'
        }}>
          <h4>📊 Sample Results:</h4>
          <ul style={{ listStyle: 'none', padding: 0 }}>
            {currentDemo.sampleResults.map((result, index) => (
              <li key={index} style={{
                background: 'rgba(255, 255, 255, 0.1)',
                padding: '0.8rem',
                margin: '0.5rem 0',
                borderRadius: '6px',
                borderLeft: '3px solid #4ecdc4'
              }}>
                ✅ {result}
              </li>
            ))}
          </ul>
        </div>
      )}

      <div style={{
        marginTop: '2rem',
        padding: '1rem',
        background: 'rgba(255, 255, 255, 0.1)',
        borderRadius: '8px'
      }}>
        <h4>🔑 Want Full Functionality?</h4>
        <p>Add your API key to <code>.env.local</code>:</p>
        <code style={{
          background: 'rgba(0, 0, 0, 0.3)',
          padding: '0.5rem',
          borderRadius: '4px',
          display: 'block',
          marginTop: '0.5rem'
        }}>
          GEMINI_API_KEY=your_api_key_here
        </code>
      </div>
    </div>
  );
};

export default DemoMode;