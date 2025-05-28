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
    // Normalize sensitivity value (0-1 range)
    const normalizedSensitivity = sensitivity / MAX_SENSITIVITY;

    // Travel time in minutes for the formulas
    const travelTimesMinutes = travelTimesSeconds.map(sec => sec / 60);

    switch(impedanceFunction) {
      case 'gaussian':
        values = travelTimesMinutes.map(t => Math.exp(-(Math.pow(t / 30, 2) / normalizedSensitivity)));
        break;
      case 'linear':
        values = travelTimesMinutes.map(t => Math.max(0, 1 - (t / 30)));
        break;
      case 'exponential':
        values = travelTimesMinutes.map(t => Math.exp(-(normalizedSensitivity * 10) * (t / 30)));
        break;
      case 'power':
        values = travelTimesMinutes.map(t => t <= 1/30 ? 1 : Math.pow((t / 30), -normalizedSensitivity * 10));
        break;
      default:
        values = travelTimesMinutes.map(t => Math.exp(-(Math.pow(t / 30, 2) / normalizedSensitivity)));
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
    ctx.fillText('Secondes', width / 2, height - 10);

    // Draw Y-axis ticks and labels
    ctx.textAlign = 'right';
    for (let i = 0; i <= 10; i++) {
      const y = height - padding - (i * (height - 2 * padding) / 10);
      ctx.beginPath();
      ctx.moveTo(padding - 5, y);
      ctx.lineTo(padding, y);
      ctx.stroke();
      ctx.fillText(`${i * 10}%`, padding - 8, y + 4);
    }

    // Draw X-axis ticks and labels
    ctx.textAlign = 'center';
    // We want to show labels at regular intervals
    const intervals = [1, 26, 51, 76, 101, 126, 151, 176, 201, 226, 251, 276, 301, 326,
                      351, 376, 401, 426, 451, 476, 501, 526, 551, 576, 601, 626, 651,
                      676, 701, 726, 751, 776, 801, 826, 851, 876, 901, 926, 951, 976,
                      1001, 1026, 1051, 1076, 1101, 1126, 1151, 1176];
                      
    const xScale = (width - 2 * padding) / DISPLAY_MAX_SEC;
    intervals.forEach(sec => {
      const x = padding + (sec * xScale);
      ctx.beginPath();
      ctx.moveTo(x, height - padding);
      ctx.lineTo(x, height - padding + 5);
      ctx.stroke();
      ctx.fillText(`${sec}`, x, height - padding + 20);
    });

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
              `f(t) = exp(-(t/30)²/β̂)` : 
            impedanceFunction === 'linear' ? 
              `f(t) = 1 - (t/30) for t ≤ 30, 0 otherwise` :
            impedanceFunction === 'exponential' ? 
              `f(t) = exp(-10β̂·(t/30))` : 
              `f(t) = 1 for t ≤ 1, (t/30)^(-10β̂) otherwise`
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