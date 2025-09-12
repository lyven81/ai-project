import React, { useState, useEffect } from 'react';

const PosePerfectDemoMode: React.FC = () => {
  const [currentPose, setCurrentPose] = useState('squat');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [formScore, setFormScore] = useState(85);

  const poses = {
    squat: {
      name: 'Squat Analysis',
      feedback: ['Keep your back straight', 'Lower your hips more', 'Great depth!'],
      score: 85,
      color: '#4CAF50'
    },
    pushup: {
      name: 'Push-up Form',
      feedback: ['Maintain plank position', 'Lower chest to ground', 'Excellent alignment!'],
      score: 92,
      color: '#2196F3'
    },
    plank: {
      name: 'Plank Hold',
      feedback: ['Engage your core', 'Keep hips level', 'Perfect form!'],
      score: 88,
      color: '#FF9800'
    }
  };

  useEffect(() => {
    const interval = setInterval(() => {
      const poseKeys = Object.keys(poses);
      const currentIndex = poseKeys.indexOf(currentPose);
      const nextIndex = (currentIndex + 1) % poseKeys.length;
      setCurrentPose(poseKeys[nextIndex]);
      setFormScore(poses[poseKeys[nextIndex] as keyof typeof poses].score);
    }, 4000);

    return () => clearInterval(interval);
  }, [currentPose]);

  const handleAnalyze = () => {
    setIsAnalyzing(true);
    setTimeout(() => setIsAnalyzing(false), 2000);
  };

  const currentPoseData = poses[currentPose as keyof typeof poses];

  return (
    <div style={{
      padding: '2rem',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      borderRadius: '12px',
      color: 'white',
      textAlign: 'center',
      maxWidth: '900px',
      margin: '2rem auto'
    }}>
      <div style={{ marginBottom: '2rem' }}>
        <h2>🏃‍♀️ Pose Perfect AI - Demo Mode</h2>
        <p>Experience real-time pose analysis and form correction!</p>
      </div>

      <div style={{
        display: 'grid',
        gridTemplateColumns: '1fr 1fr',
        gap: '2rem',
        marginBottom: '2rem'
      }}>
        {/* Virtual Camera View */}
        <div style={{
          background: 'rgba(255, 255, 255, 0.1)',
          borderRadius: '12px',
          padding: '1.5rem',
          minHeight: '300px',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center'
        }}>
          <h3>📹 Virtual Camera</h3>
          <div style={{
            width: '200px',
            height: '200px',
            background: currentPoseData.color,
            borderRadius: '10px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '4rem',
            marginBottom: '1rem',
            animation: isAnalyzing ? 'pulse 1s infinite' : 'none'
          }}>
            🏃‍♂️
          </div>
          <p><strong>{currentPoseData.name}</strong></p>
          <button
            onClick={handleAnalyze}
            disabled={isAnalyzing}
            style={{
              background: isAnalyzing ? '#666' : '#ff6b6b',
              color: 'white',
              border: 'none',
              padding: '0.8rem 1.5rem',
              borderRadius: '20px',
              cursor: isAnalyzing ? 'not-allowed' : 'pointer',
              transition: 'all 0.3s ease'
            }}
          >
            {isAnalyzing ? '🔄 Analyzing...' : '🔍 Analyze Pose'}
          </button>
        </div>

        {/* Analysis Results */}
        <div style={{
          background: 'rgba(255, 255, 255, 0.1)',
          borderRadius: '12px',
          padding: '1.5rem'
        }}>
          <h3>📊 Real-time Analysis</h3>
          
          {/* Form Score */}
          <div style={{ marginBottom: '1.5rem' }}>
            <h4>Form Score</h4>
            <div style={{
              background: 'rgba(255, 255, 255, 0.2)',
              borderRadius: '20px',
              padding: '0.5rem',
              position: 'relative',
              height: '40px'
            }}>
              <div style={{
                background: currentPoseData.color,
                borderRadius: '20px',
                height: '100%',
                width: `${formScore}%`,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                transition: 'all 1s ease'
              }}>
                <strong>{formScore}/100</strong>
              </div>
            </div>
          </div>

          {/* Feedback */}
          <div>
            <h4>💡 Live Feedback</h4>
            <div style={{ textAlign: 'left' }}>
              {currentPoseData.feedback.map((feedback, index) => (
                <div key={index} style={{
                  background: 'rgba(255, 255, 255, 0.1)',
                  padding: '0.8rem',
                  margin: '0.5rem 0',
                  borderRadius: '6px',
                  borderLeft: `3px solid ${currentPoseData.color}`
                }}>
                  {index === currentPoseData.feedback.length - 1 ? '✅' : '⚠️'} {feedback}
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Exercise Selection */}
      <div style={{
        background: 'rgba(255, 255, 255, 0.1)',
        borderRadius: '12px',
        padding: '1.5rem',
        marginBottom: '1.5rem'
      }}>
        <h3>🏋️ Exercise Library</h3>
        <div style={{ display: 'flex', justifyContent: 'center', gap: '1rem', marginTop: '1rem' }}>
          {Object.entries(poses).map(([key, pose]) => (
            <button
              key={key}
              onClick={() => setCurrentPose(key)}
              style={{
                background: key === currentPose ? pose.color : 'rgba(255, 255, 255, 0.2)',
                color: 'white',
                border: 'none',
                padding: '0.8rem 1.5rem',
                borderRadius: '20px',
                cursor: 'pointer',
                transition: 'all 0.3s ease'
              }}
            >
              {pose.name}
            </button>
          ))}
        </div>
      </div>

      {/* Features */}
      <div style={{
        background: 'rgba(255, 255, 255, 0.1)',
        borderRadius: '12px',
        padding: '1.5rem'
      }}>
        <h3>🎯 AI Features Demonstrated</h3>
        <div style={{ display: 'flex', flexWrap: 'wrap', justifyContent: 'center', gap: '0.5rem', marginTop: '1rem' }}>
          {['Real-time Tracking', 'Form Analysis', 'Score Calculation', 'Live Feedback', 'Exercise Detection', 'Progress Analytics'].map((feature, index) => (
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

      <div style={{ marginTop: '2rem', padding: '1rem', background: 'rgba(255, 255, 255, 0.1)', borderRadius: '8px' }}>
        <h4>🔑 Enable Full Camera Mode</h4>
        <p>Add your Gemini API key to activate real computer vision!</p>
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

      <style>{`
        @keyframes pulse {
          0% { transform: scale(1); }
          50% { transform: scale(1.05); }
          100% { transform: scale(1); }
        }
      `}</style>
    </div>
  );
};

export default PosePerfectDemoMode;