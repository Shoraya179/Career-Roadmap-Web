import React, { useState } from 'react';
import { ReactFlow, Background, Controls } from '@xyflow/react';
import '@xyflow/react/dist/style.css';

// Sample career roadmap milestones to get you started
const defaultNodes = [
  { id: '1', position: { x: 250, y: 50 }, data: { label: '🎯 Dream Goal: Cloud Security Engineer' } },
  { id: '2', position: { x: 250, y: 150 }, data: { label: 'Step 1: Master Linux & Networking' } },
  { id: '3', position: { x: 250, y: 250 }, data: { label: 'Step 2: Build Hands-on Cloud Projects' } },
  { id: '4', position: { x: 250, y: 350 }, data: { label: 'Step 3: Junior Cloud Analyst Role' } },
];

const defaultEdges = [
  { id: 'e1-2', source: '1', target: '2' },
  { id: 'e2-3', source: '2', target: '3' },
  { id: 'e3-4', source: '3', target: '4' },
];

export default function App() {
  const [roleInput, setRoleInput] = useState('');
  const [nodes, setNodes] = useState(defaultNodes);
  const [edges, setEdges] = useState(defaultEdges);

  const handleGenerate = (e) => {
    e.preventDefault();
    if (!roleInput.trim()) return;

    // Updates the top milestone with what the user typed
    setNodes((prev) => [
      { id: '1', position: { x: 250, y: 50 }, data: { label: `🎯 Dream Goal: ${roleInput}` } },
      ...prev.slice(1),
    ]);
  };

  return (
    <div style={{ width: '100vw', height: '100vh', display: 'flex', flexDirection: 'column', fontFamily: 'sans-serif' }}>
      {/* Top Header & Search Bar */}
      <div style={{ padding: '16px', background: '#1e293b', color: '#fff', display: 'flex', gap: '12px', alignItems: 'center' }}>
        <h2 style={{ margin: 0, fontSize: '18px' }}>Career Roadmapper AI</h2>
        <form onSubmit={handleGenerate} style={{ display: 'flex', gap: '8px', flex: 1, maxWidth: '600px' }}>
          <input
            type="text"
            placeholder="e.g. Frontend Engineer at a Fintech startup..."
            value={roleInput}
            onChange={(e) => setRoleInput(e.target.value)}
            style={{ flex: 1, padding: '8px 12px', borderRadius: '6px', border: '1px solid #475569' }}
          />
          <button type="submit" style={{ padding: '8px 16px', background: '#2563eb', color: '#fff', border: 'none', borderRadius: '6px', cursor: 'pointer' }}>
            Generate Path
          </button>
        </form>
      </div>

      {/* Interactive Visual Roadmap Canvas */}
      <div style={{ flex: 1 }}>
        <ReactFlow nodes={nodes} edges={edges} fitView>
          <Background />
          <Controls />
        </ReactFlow>
      </div>
    </div>
  );
}