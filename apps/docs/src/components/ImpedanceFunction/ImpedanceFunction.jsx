import React, { useEffect, useRef, useState } from 'react';

export default function ImpedanceFunction({ initialFunction = 'gaussian', initialSensitivity = 300000 }) {
  const [impedanceFunction, setImpedanceFunction] = useState(initialFunction);
  const [sensitivity, setSensitivity] = useState(initialSensitivity);
  const canvasRef = useRef(null);

  // Define the canvas dimensions
  const width = 600;
  const height = 400;
  const padding = 40;
  
  // Max travel time in seconds (30 minutes = 1800 seconds)
  const MAX_TRAVEL_TIME_SEC = 1800;
  // Display up to 1176 seconds on the x-axis (as shown in the reference image)
  const DISPLAY_MAX_SEC = 1176;
  // Max sensitivity value
  const MAX_SENSITIVITY = 1000000;

  // Calculate values based on the selected function and sensitivity
  const calculateValues = () => {
    // Generate data points every 25 seconds
    const travelTimesSeconds = [];
    for (let t = 0; t <= DISPLAY_MAX_SEC; t += 25) {
      travelTimesSeconds.push(t);
    }
    
    let values = [];
    // Travel time in minutes for the formulas
    const travelTimesMinutes = travelTimesSeconds.map(sec => sec / 60);

    switch(impedanceFunction) {
      case 'gaussian':
        // Gaussian: exp(-β * t²) where β controls the decay rate
        const beta = sensitivity / MAX_SENSITIVITY; // normalized sensitivity
        values = travelTimesMinutes.map(t => Math.exp(-beta * 10 * Math.pow(t, 2)));
        break;
      case 'linear':
        // Linear: max(0, 1 - t/T) where T is maximum travel time
        values = travelTimesMinutes.map(t => Math.max(0, 1 - (t / 30)));
        break;
      case 'exponential':
        // Exponential: exp(-β * t)
        const expBeta = (sensitivity / MAX_SENSITIVITY) * 5; // scaling factor
        values = travelTimesMinutes.map(t => Math.exp(-expBeta * t));
        break;
      case 'power':
        // Power: t^(-β) for t > 0, 1 for t = 0
        const powerBeta = (sensitivity / MAX_SENSITIVITY) * 2;
        values = travelTimesMinutes.map(t => t <= 0.01 ? 1 : Math.pow(t + 0.01, -powerBeta));
        break;
      default:
        const defaultBeta = sensitivity / MAX_SENSITIVITY;
        values = travelTimesMinutes.map(t => Math.exp(-defaultBeta * 10 * Math.pow(t, 2)));
    }

    return { travelTimesSeconds, values };
  };

  // Draw the graph on the canvas
  const drawGraph = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, width, height);

    const { travelTimesSeconds, values } = calculateValues();

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
    ctx.fillText('Seconds', width / 2, height - 10);

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
    const xScale = (width - 2 * padding) / DISPLAY_MAX_SEC;
    
    // Show ticks every 100 seconds for cleaner display
    for (let sec = 0; sec <= DISPLAY_MAX_SEC; sec += 100) {
      const x = padding + (sec * xScale);
      ctx.beginPath();
      ctx.moveTo(x, height - padding);
      ctx.lineTo(x, height - padding + 5);
      ctx.stroke();
      
      // Only show labels for major ticks to avoid crowding
      if (sec % 200 === 0 || sec === DISPLAY_MAX_SEC) {
        ctx.fillText(`${sec}`, x, height - padding + 20);
      }
    }

    // Draw the graph
    ctx.beginPath();
    
    for (let i = 0; i < travelTimesSeconds.length; i++) {
      const x = padding + travelTimesSeconds[i] * xScale;
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
              `f(t) = exp(-β̂ × 10 × t²)` : 
            impedanceFunction === 'linear' ? 
              `f(t) = max(0, 1 - t/30)` :
            impedanceFunction === 'exponential' ? 
              `f(t) = exp(-β̂ × 5 × t)` : 
              `f(t) = (t + 0.01)^(-β̂ × 2)`
          }
          <br/>
          <small>where β̂ = β/{MAX_SENSITIVITY.toLocaleString()} is the normalized sensitivity (0-1 scale)</small>
          <br/>
          <small>and t is travel time in minutes (converted from seconds on x-axis)</small>
        </p>
      </div>
    </div>
  );
}