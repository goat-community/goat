import React, { useEffect, useRef, useState } from 'react';

export default function ImpedanceFunction({ initialFunction = 'gaussian', initialSensitivity = 300000 }) {
  const [impedanceFunction, setImpedanceFunction] = useState(initialFunction);
  const [sensitivity, setSensitivity] = useState(initialSensitivity);
  const canvasRef = useRef(null);

  // Define the canvas dimensions
  const width = 600;
  const height = 400;
  const padding = 40;
  
  // Max travel time in minutes
  const MAX_TRAVEL_TIME_MIN = 30;
  // Display up to approximately 20 minutes on the x-axis
  const DISPLAY_MAX_MIN = 20;
  // Max sensitivity value
  const MAX_SENSITIVITY = 1000000;

  // Calculate values based on the selected function and sensitivity
  const calculateValues = () => {
    // Generate data points for minutes
    const travelTimesMinutes = [];
    for (let t = 0; t <= DISPLAY_MAX_MIN; t += 0.5) {
      travelTimesMinutes.push(t);
    }
    
    let values = [];

    switch(impedanceFunction) {
      case 'gaussian':
        // For gaussian (gravity): normalize travel time by 30 minutes and sensitivity by 1 million
        const normalizedSensitivity = sensitivity / MAX_SENSITIVITY;
        values = travelTimesMinutes.map(t => {
          const normalizedTime = t / MAX_TRAVEL_TIME_MIN;
          return Math.exp(-normalizedSensitivity * 10 * Math.pow(normalizedTime, 2));
        });
        break;
      case 'linear':
        // Linear: max(0, 1 - t/T) where T is maximum travel time
        // Linear function doesn't depend on sensitivity
        values = travelTimesMinutes.map(t => Math.max(0, 1 - (t / MAX_TRAVEL_TIME_MIN)));
        break;
      case 'exponential':
        // Exponential: exp(-β * t) - normalize travel time by 30 minutes and sensitivity by 1 million
        const expNormalizedSensitivity = sensitivity / MAX_SENSITIVITY;
        values = travelTimesMinutes.map(t => {
          const normalizedTime = t / MAX_TRAVEL_TIME_MIN;
          return Math.exp(-expNormalizedSensitivity * 5 * normalizedTime);
        });
        break;
      case 'power':
        // Power: normalize the power coefficient by max sensitivity (1 million), don't normalize travel time
        const powerCoefficient = sensitivity / MAX_SENSITIVITY;
        values = travelTimesMinutes.map(t => t <= 0.01 ? 1 : Math.pow(t + 0.01, -powerCoefficient * 2));
        break;
      default:
        const defaultNormalizedSensitivity = sensitivity / MAX_SENSITIVITY;
        values = travelTimesMinutes.map(t => {
          const normalizedTime = t / MAX_TRAVEL_TIME_MIN;
          return Math.exp(-defaultNormalizedSensitivity * 10 * Math.pow(normalizedTime, 2));
        });
    }

    return { travelTimesMinutes, values };
  };

  // Draw the graph on the canvas
  const drawGraph = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, width, height);

    const { travelTimesMinutes, values } = calculateValues();

    // Draw axes
    ctx.beginPath();
    ctx.moveTo(padding, padding);
    ctx.lineTo(padding, height - padding);
    ctx.lineTo(width - padding, height - padding);
    ctx.strokeStyle = '#333';
    ctx.lineWidth = 2;
    ctx.stroke();

    // Draw title
    ctx.fillStyle = '#333';
    ctx.font = '16px Arial';
    ctx.textAlign = 'center';
    ctx.fillText(`${impedanceFunction.charAt(0).toUpperCase() + impedanceFunction.slice(1)} impedance function`, width / 2, padding / 2);

    // Draw labels
    ctx.font = '12px Arial';
    
    // Y-axis label
    ctx.save();
    ctx.translate(15, height / 2);
    ctx.rotate(-Math.PI / 2);
    ctx.fillText('Willingness to walk', 0, 0);
    ctx.restore();
    
    // X-axis label
    ctx.fillText('Minutes', width / 2, height - 10);

    // Draw Y-axis ticks and labels
    ctx.textAlign = 'right';
    for (let i = 0; i <= 12; i++) {
      const y = height - padding - (i * (height - 2 * padding) / 12);
      ctx.beginPath();
      ctx.moveTo(padding - 5, y);
      ctx.lineTo(padding, y);
      ctx.stroke();
      ctx.fillText(`${i * 10}%`, padding - 8, y + 4);
    }

    // Draw X-axis ticks and labels
    ctx.textAlign = 'center';
    const xScale = (width - 2 * padding) / DISPLAY_MAX_MIN;
    
    // Show ticks every 2 minutes for cleaner display
    for (let min = 0; min <= DISPLAY_MAX_MIN; min += 2) {
      const x = padding + (min * xScale);
      ctx.beginPath();
      ctx.moveTo(x, height - padding);
      ctx.lineTo(x, height - padding + 5);
      ctx.stroke();
      
      // Show labels for major ticks
      ctx.fillText(`${min}`, x, height - padding + 20);
    }

    // Draw the graph
    ctx.beginPath();
    
    for (let i = 0; i < travelTimesMinutes.length; i++) {
      const x = padding + travelTimesMinutes[i] * xScale;
      const y = height - padding - values[i] * (height - 2 * padding);
      
      if (i === 0) {
        ctx.moveTo(x, y);
      } else {
        ctx.lineTo(x, y);
      }
    }

    ctx.strokeStyle = '#0066cc';
    ctx.lineWidth = 3;
    ctx.stroke();
  };

  // Update the graph when impedance function or sensitivity changes
  useEffect(() => {
    drawGraph();
  }, [impedanceFunction, sensitivity]);

  return (
    <div style={{ marginBottom: '30px' }}>
      <div style={{ marginBottom: '20px' }}>
        <label style={{ marginRight: '10px', fontWeight: 'bold' }}>Impedance Function:</label>
        <select 
          value={impedanceFunction} 
          onChange={(e) => setImpedanceFunction(e.target.value)}
          style={{ padding: '8px', borderRadius: '4px', marginRight: '20px' }}
        >
          <option value="gaussian">Gaussian</option>
          <option value="linear">Linear</option>
          <option value="exponential">Exponential</option>
          <option value="power">Power</option>
        </select>
        
        {/* Only show sensitivity slider for functions that depend on it */}
        {impedanceFunction !== 'linear' && (
          <>
            <label style={{ marginRight: '10px', fontWeight: 'bold' }}>Sensitivity (β):</label>
            <input 
              type="range" 
              min="10000" 
              max={MAX_SENSITIVITY} 
              step="10000" 
              value={sensitivity} 
              onChange={(e) => setSensitivity(Number(e.target.value))} 
              style={{ width: '150px', verticalAlign: 'middle' }}
            />
            <span style={{ marginLeft: '10px' }}>{sensitivity.toLocaleString()}</span>
          </>
        )}
      </div>
      
      <canvas ref={canvasRef} width={width} height={height} style={{ border: '1px solid #ddd', borderRadius: '4px' }} />
      
      <div style={{ marginTop: '10px', fontSize: '14px', color: '#666' }}>
        <p>
          The graph shows how the willingness to walk decreases with increasing travel time based on the selected
          impedance function and sensitivity value (β).
        </p>
        <p>
          <strong>Current function:</strong> {impedanceFunction.charAt(0).toUpperCase() + impedanceFunction.slice(1)}
          <br />
          <strong>Formula:</strong> {
            impedanceFunction === 'gaussian' ? 
              `f(t) = exp(-β̂ × 10 × (t/30)²)` : 
            impedanceFunction === 'linear' ? 
              `f(t) = max(0, 1 - t/30)` :
            impedanceFunction === 'exponential' ? 
              `f(t) = exp(-β̂ × 5 × (t/30))` : 
              `f(t) = (t + 0.01)^(-β̂ × 2)`
          }
          <br/>
          {impedanceFunction !== 'linear' && (
            <>
              <small>where β̂ = β/{MAX_SENSITIVITY.toLocaleString()} is the normalized sensitivity (0-1 scale)</small>
              <br/>
            </>
          )}
          <small>and t is travel time in minutes</small>
          {impedanceFunction === 'gaussian' && <small><br/>Travel time is normalized by 30 minutes for Gaussian function</small>}
          {impedanceFunction === 'exponential' && <small><br/>Travel time is normalized by 30 minutes for Exponential function</small>}
          {impedanceFunction === 'power' && <small><br/>Power coefficient is normalized by max sensitivity, travel time is not normalized</small>}
        </p>
      </div>
    </div>
  );
}