import React, { useEffect, useRef, useState } from 'react';

export default function ImpedanceFunction({ initialFunction = 'gaussian', initialSensitivity = 300000 }) {
  const [impedanceFunction, setImpedanceFunction] = useState(initialFunction);
  const [sensitivity, setSensitivity] = useState(initialSensitivity);
  const canvasRef = useRef(null);

  // Define the canvas dimensions
  const width = 600;
  const height = 400;
  const padding = 40;

  // Calculate values based on the selected function and sensitivity
  const calculateValues = () => {
    const travelTimes = Array.from({ length: 31 }, (_, i) => i); // 0 to 30 minutes
    let values = [];
    // Normalize sensitivity value (0-1 range)
    const normalizedSensitivity = sensitivity / 1000000;

    switch(impedanceFunction) {
      case 'gaussian':
        values = travelTimes.map(t => Math.exp(-(Math.pow(t / 30, 2) / normalizedSensitivity)));
        break;
      case 'linear':
        values = travelTimes.map(t => t <= 30 ? 1 - (t / 30) : 0);
        break;
      case 'exponential':
        values = travelTimes.map(t => Math.exp(-(normalizedSensitivity * 10) * (t / 30)));
        break;
      case 'power':
        values = travelTimes.map(t => t <= 1 ? 1 : Math.pow((t / 30), -normalizedSensitivity * 10));
        break;
      default:
        values = travelTimes.map(t => Math.exp(-(Math.pow(t / 30, 2) / normalizedSensitivity)));
    }

    return { travelTimes, values };
  };

  // Draw the graph on the canvas
  const drawGraph = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, width, height);

    const { travelTimes, values } = calculateValues();

    // Draw axes
    ctx.beginPath();
    ctx.moveTo(padding, padding);
    ctx.lineTo(padding, height - padding);
    ctx.lineTo(width - padding, height - padding);
    ctx.strokeStyle = '#333';
    ctx.lineWidth = 2;
    ctx.stroke();

    // Draw labels
    ctx.fillStyle = '#333';
    ctx.font = '12px Arial';
    ctx.textAlign = 'center';
    
    // Y-axis label
    ctx.save();
    ctx.translate(15, height / 2);
    ctx.rotate(-Math.PI / 2);
    ctx.fillText('Willingness to walk/cycle', 0, 0);
    ctx.restore();
    
    // X-axis label
    ctx.fillText('Travel time (minutes)', width / 2, height - 10);

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
    const xStep = (width - 2 * padding) / 30;
    for (let i = 0; i <= 30; i+=5) {
      const x = padding + i * xStep;
      ctx.beginPath();
      ctx.moveTo(x, height - padding);
      ctx.lineTo(x, height - padding + 5);
      ctx.stroke();
      ctx.fillText(`${i}`, x, height - padding + 20);
    }

    // Draw the graph
    ctx.beginPath();
    const xScale = (width - 2 * padding) / 30;
    const yScale = (height - 2 * padding);

    for (let i = 0; i < travelTimes.length; i++) {
      const x = padding + travelTimes[i] * xScale;
      const y = height - padding - values[i] * yScale;
      
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
          max="1000000" 
          step="10000" 
          value={sensitivity} 
          onChange={(e) => setSensitivity(Number(e.target.value))} 
          style={{ width: '150px', verticalAlign: 'middle' }}
        />
        <span style={{ marginLeft: '10px' }}>{sensitivity}</span>
      </div>
      
      <canvas ref={canvasRef} width={width} height={height} style={{ border: '1px solid #ddd', borderRadius: '4px' }} />
      
      <div style={{ marginTop: '10px', fontSize: '14px', color: '#666' }}>
        <p>
          The graph shows how the willingness to walk/cycle decreases with increasing travel time based on the selected
          impedance function and sensitivity value (β).
        </p>
        <p>
          <strong>Current function:</strong> {impedanceFunction.charAt(0).toUpperCase() + impedanceFunction.slice(1)}
          <br />
          <strong>Formula:</strong> {impedanceFunction === 'gaussian' ? 'f(t) = exp(-(t/30)²/β̂)' : 
                        impedanceFunction === 'linear' ? 'f(t) = 1 - (t/30) for t ≤ 30, 0 otherwise' :
                        impedanceFunction === 'exponential' ? 'f(t) = exp(-10β̂·(t/30))' : 
                        'f(t) = 1 for t ≤ 1, (t/30)^(-10β̂) otherwise'}
          <br/>
          <small>where β̂ = β/1000000 is the normalized sensitivity (0-1)</small>
        </p>
      </div>
    </div>
  );
}