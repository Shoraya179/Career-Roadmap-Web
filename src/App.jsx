import React, { useState, useEffect, useMemo, useCallback } from 'react';
import {
  ReactFlow,
  Background,
  Controls,
  applyNodeChanges,
  applyEdgeChanges,
  Handle,
  Position,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import {
  Compass,
  FileSearch,
  CheckCircle2,
  Sparkles,
  TrendingUp,
  MessageSquare,
  AlertCircle,
  Play,
  RotateCcw,
  Send,
  ExternalLink,
  ShieldCheck,
  Award,
  Layers,
  ChevronRight,
  Info,
} from 'lucide-react';
import './App.css';

// -------------------------------------------------------------
// Custom Node for ReactFlow
// -------------------------------------------------------------
function CustomMilestoneNode({ data }) {
  const isGoal = data.stepNumber === 0;
  return (
    <div
      style={{
        padding: '12px 16px',
        borderRadius: '10px',
        background: isGoal ? 'linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%)' : '#ffffff',
        color: isGoal ? '#ffffff' : '#0f172a',
        border: isGoal ? 'none' : '1px solid #cbd5e1',
        boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
        minWidth: '220px',
        maxWidth: '280px',
        fontSize: '12px',
      }}
    >
      <Handle type="target" position={Position.Top} style={{ background: '#6366f1' }} />
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
        <span
          style={{
            fontSize: '10px',
            fontWeight: '700',
            textTransform: 'uppercase',
            color: isGoal ? '#e0e7ff' : '#6366f1',
          }}
        >
          {data.stage || `Step ${data.stepNumber}`}
        </span>
        {data.duration && (
          <span style={{ fontSize: '10px', color: isGoal ? '#c7d2fe' : '#64748b' }}>
            {data.duration}
          </span>
        )}
      </div>
      <div style={{ fontWeight: '700', fontSize: '13px', lineHeight: '1.3', marginBottom: '6px' }}>
        {data.label}
      </div>
      {data.skills && data.skills.length > 0 && (
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '3px', marginTop: '6px' }}>
          {data.skills.slice(0, 3).map((s, idx) => (
            <span
              key={idx}
              style={{
                fontSize: '9px',
                padding: '2px 5px',
                borderRadius: '4px',
                background: isGoal ? 'rgba(255,255,255,0.2)' : '#f1f5f9',
                color: isGoal ? '#ffffff' : '#475569',
              }}
            >
              {s}
            </span>
          ))}
        </div>
      )}
      <Handle type="source" position={Position.Bottom} style={{ background: '#6366f1' }} />
    </div>
  );
}

// -------------------------------------------------------------
// Sample Job Descriptions for Instant Testing
// -------------------------------------------------------------
const SAMPLE_JDS = {
  cloudSecurity: `We are seeking a Cloud Security Engineer to safeguard our multi-cloud infrastructure.
Responsibilities:
- Implement and manage AWS IAM policies using least-privilege principles.
- Automate security compliance audits and vulnerability scanning using Terraform and Python.
- Configure VPC peering, Security Groups, and CloudTrail monitoring.
- Work closely with DevOps teams to embed Shift-Left security into GitHub Actions CI/CD pipelines.
Requirements:
- 2+ years of hands-on experience with AWS / Azure.
- Strong proficiency in Linux system administration and Bash scripting.
- Understanding of Docker container security and Kubernetes fundamentals.
- Familiarity with CIS Benchmarks and SOC2 compliance standards.`,
  fullStack: `Looking for a Full Stack Developer (React / FastAPI / Node).
Responsibilities:
- Design and implement responsive client-facing applications using React and modern CSS.
- Build resilient backend microservices with RESTful APIs and PostgreSQL databases.
- Write unit and integration tests to ensure code quality and deployment stability.
- Collaborate with product designers and engineers in an Agile sprint environment.
Requirements:
- Proficiency in JavaScript/TypeScript, React 18+, and state management.
- Experience with Python (FastAPI/Flask) or Node.js.
- Familiarity with Docker, Git workflows, and CI/CD pipelines.`
};

export default function App() {
  // Navigation
  const [activeTab, setActiveTab] = useState('roadmap'); // 'roadmap' | 'analyzer' | 'assessment' | 'adaptive' | 'counselor'
  
  // Health & Server Status
  const [health, setHealth] = useState({
    aiConfigured: false,
    model: 'gemini-2.5-flash',
    maskedKey: '',
    mode: 'Checking...',
    loading: true,
  });
  const [showConfigModal, setShowConfigModal] = useState(false);

  // 1. Roadmap State
  const [roleInput, setRoleInput] = useState('Cloud Security Engineer');
  const [levelInput, setLevelInput] = useState('Beginner');
  const [timeframeInput, setTimeframeInput] = useState('6 Months');
  const [roadmapData, setRoadmapData] = useState(null);
  const [roadmapLoading, setRoadmapLoading] = useState(false);
  const [nodes, setNodes] = useState([]);
  const [edges, setEdges] = useState([]);
  const [completedMilestones, setCompletedMilestones] = useState({});

  // 2. Job Analyzer State
  const [jdText, setJdText] = useState(SAMPLE_JDS.cloudSecurity);
  const [userSkillsText, setUserSkillsText] = useState('Linux, Bash scripting, Basic Python');
  const [analyzerData, setAnalyzerData] = useState(null);
  const [analyzerLoading, setAnalyzerLoading] = useState(false);

  // 3. Assessment & Quiz State
  const [assessmentRole, setAssessmentRole] = useState('Cloud Security Engineer');
  const [assessmentDifficulty, setAssessmentDifficulty] = useState('Beginner');
  const [assessmentData, setAssessmentData] = useState(null);
  const [assessmentLoading, setAssessmentLoading] = useState(false);
  const [userAnswers, setUserAnswers] = useState({});
  const [quizSubmitted, setQuizSubmitted] = useState(false);
  const [quizScore, setQuizScore] = useState(null);

  // 4. Adaptive Recommendations State
  const [adaptiveData, setAdaptiveData] = useState(null);
  const [adaptiveLoading, setAdaptiveLoading] = useState(false);

  // 5. Counselor Chat State
  const [chatMessages, setChatMessages] = useState([
    {
      role: 'assistant',
      content: "Hello! I'm your CareerForge AI Counselor. I can analyze your roadmap, identify your skill gaps, and give you tactical strategies for interviews and career pivots. What's on your mind today?"
    }
  ]);
  const [chatInput, setChatInput] = useState('');
  const [chatLoading, setChatLoading] = useState(false);
  const [suggestedQuestions, setSuggestedQuestions] = useState([
    "What portfolio projects will make me stand out?",
    "How can I prepare for technical interviews?",
    "What are the best strategies to transition into this role?"
  ]);

  const nodeTypes = useMemo(() => ({ customMilestone: CustomMilestoneNode }), []);

  const checkHealth = useCallback(async () => {
    try {
      const res = await fetch('/api/health');
      if (res.ok) {
        const data = await res.json();
        setHealth({ ...data, loading: false });
      } else {
        setHealth({ aiConfigured: false, model: 'gemini-2.5-flash', mode: 'Offline Template Fallback', loading: false });
      }
    } catch {
      setHealth({ aiConfigured: false, model: 'gemini-2.5-flash', mode: 'Offline Template Fallback', loading: false });
    }
  }, []);

  const handleGenerateRoadmap = useCallback(async (e) => {
    if (e) e.preventDefault();
    if (!roleInput.trim()) return;

    setRoadmapLoading(true);
    try {
      const res = await fetch('/api/roadmap/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          role: roleInput,
          level: levelInput,
          timeframe: timeframeInput,
        }),
      });
      const data = await res.json();
      setRoadmapData(data);

      const formattedNodes = (data.nodes || []).map((n) => ({
        ...n,
        type: 'customMilestone',
      }));
      setNodes(formattedNodes);
      setEdges(data.edges || []);
      setAssessmentRole(data.role || roleInput);
    } catch (err) {
      console.error('Roadmap error:', err);
    } finally {
      setRoadmapLoading(false);
    }
  }, [roleInput, levelInput, timeframeInput]);

  useEffect(() => {
    checkHealth();
  }, [checkHealth]);

  useEffect(() => {
    handleGenerateRoadmap();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const onNodesChange = (changes) => setNodes((nds) => applyNodeChanges(changes, nds));
  const onEdgesChange = (changes) => setEdges((eds) => applyEdgeChanges(changes, eds));

  const toggleMilestoneCompleted = (id) => {
    setCompletedMilestones((prev) => ({
      ...prev,
      [id]: !prev[id],
    }));
  };

  // -------------------------------------------------------------
  // Feature 2: Job Description Analysis
  // -------------------------------------------------------------
  const handleAnalyzeJob = async (e) => {
    if (e) e.preventDefault();
    if (!jdText.trim()) return;

    setAnalyzerLoading(true);
    try {
      const res = await fetch('/api/job/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          jobDescription: jdText,
          userSkills: userSkillsText,
        }),
      });
      const data = await res.json();
      setAnalyzerData(data);
    } catch (err) {
      console.error('Job analysis error:', err);
    } finally {
      setAnalyzerLoading(false);
    }
  };

  // -------------------------------------------------------------
  // Feature 3: Skill Assessment Diagnostic Quiz
  // -------------------------------------------------------------
  const handleGenerateAssessment = async (e) => {
    if (e) e.preventDefault();
    setAssessmentLoading(true);
    setUserAnswers({});
    setQuizSubmitted(false);
    setQuizScore(null);

    try {
      const res = await fetch('/api/assessment/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          role: assessmentRole,
          difficulty: assessmentDifficulty,
          numQuestions: 5,
        }),
      });
      const data = await res.json();
      setAssessmentData(data);
    } catch (err) {
      console.error('Assessment generation error:', err);
    } finally {
      setAssessmentLoading(false);
    }
  };

  const handleSelectOption = (questionId, optionIndex) => {
    if (quizSubmitted) return;
    setUserAnswers((prev) => ({
      ...prev,
      [questionId]: optionIndex,
    }));
  };

  const handleSubmitQuiz = () => {
    if (!assessmentData || !assessmentData.questions) return;
    let correctCount = 0;
    const questions = assessmentData.questions;
    const correctSkills = [];
    const missedSkills = [];
    const detailed = [];

    questions.forEach((q) => {
      const userSelected = userAnswers[q.id];
      const isCorrect = userSelected === q.correctAnswerIndex;
      if (isCorrect) {
        correctCount += 1;
        correctSkills.push(q.testedSkill);
      } else {
        missedSkills.push(q.testedSkill);
      }
      detailed.push({
        question: q.question,
        selectedAnswer: q.options[userSelected] || 'Unanswered',
        correctAnswer: q.options[q.correctAnswerIndex],
        explanation: q.explanation,
        skill: q.testedSkill,
        isCorrect,
      });
    });

    const calculatedScore = {
      score: correctCount,
      total: questions.length,
      percentage: Math.round((correctCount / questions.length) * 100),
      correctSkills,
      missedSkills,
      detailed,
    };

    setQuizScore(calculatedScore);
    setQuizSubmitted(true);
  };

  // -------------------------------------------------------------
  // Feature 4: Adaptive Learning Recommendations
  // -------------------------------------------------------------
  const handleTriggerAdaptivePlan = async (scoreObj = quizScore) => {
    if (!scoreObj) return;
    setAdaptiveLoading(true);
    setActiveTab('adaptive');

    try {
      const res = await fetch('/api/assessment/adapt', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          role: assessmentRole,
          score: scoreObj.score,
          totalQuestions: scoreObj.total,
          correctSkills: scoreObj.correctSkills,
          missedSkills: scoreObj.missedSkills,
          detailedResults: scoreObj.detailed,
        }),
      });
      const data = await res.json();
      setAdaptiveData(data);
    } catch (err) {
      console.error('Adaptive plan error:', err);
    } finally {
      setAdaptiveLoading(false);
    }
  };

  // -------------------------------------------------------------
  // Feature 5: Contextual AI Career Guidance
  // -------------------------------------------------------------
  const handleSendMessage = async (customPrompt) => {
    const textToSend = (customPrompt || chatInput).trim();
    if (!textToSend || chatLoading) return;

    const newMessages = [...chatMessages, { role: 'user', content: textToSend }];
    setChatMessages(newMessages);
    setChatInput('');
    setChatLoading(true);

    const contextPayload = {
      currentRole: roleInput,
      roadmapOverview: roadmapData?.overview || '',
      assessmentScore: quizScore ? quizScore.percentage : null,
      topGaps: analyzerData?.skillGaps ? analyzerData.skillGaps.map((g) => g.skill).slice(0, 3) : [],
    };

    try {
      const res = await fetch('/api/guidance/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          messages: newMessages,
          context: contextPayload,
        }),
      });
      const data = await res.json();
      setChatMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: data.reply,
          isAiGenerated: data.isAiGenerated,
          modelUsed: data.modelUsed,
          fallbackReason: data.fallbackReason,
        },
      ]);
      if (data.suggestedNextQuestions && data.suggestedNextQuestions.length > 0) {
        setSuggestedQuestions(data.suggestedNextQuestions);
      }
    } catch (err) {
      console.error('Chat error:', err);
      setChatMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: "I encountered an issue connecting with the AI engine. Please verify the server is running.",
          isAiGenerated: false,
        },
      ]);
    } finally {
      setChatLoading(false);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', minHeight: '100vh', width: '100%' }}>
      {/* ============================================================== */}
      {/* 1. Header with Live AI Status Indicator */}
      {/* ============================================================== */}
      <header className="app-header">
        <div className="brand-section">
          <div className="brand-logo-icon">CF</div>
          <div>
            <h1 className="brand-title">CareerForge AI</h1>
            <div className="brand-subtitle">Real Generative AI Career Navigator</div>
          </div>
        </div>

        {/* Tab Navigation */}
        <nav className="nav-tabs">
          <button
            className={`nav-tab-btn ${activeTab === 'roadmap' ? 'active' : ''}`}
            onClick={() => setActiveTab('roadmap')}
          >
            <Compass size={16} /> Roadmap Canvas
          </button>
          <button
            className={`nav-tab-btn ${activeTab === 'analyzer' ? 'active' : ''}`}
            onClick={() => setActiveTab('analyzer')}
          >
            <FileSearch size={16} /> Job Analyzer
          </button>
          <button
            className={`nav-tab-btn ${activeTab === 'assessment' ? 'active' : ''}`}
            onClick={() => setActiveTab('assessment')}
          >
            <ShieldCheck size={16} /> Skill Quiz
          </button>
          <button
            className={`nav-tab-btn ${activeTab === 'adaptive' ? 'active' : ''}`}
            onClick={() => setActiveTab('adaptive')}
          >
            <TrendingUp size={16} /> Adaptive Learning
          </button>
          <button
            className={`nav-tab-btn ${activeTab === 'counselor' ? 'active' : ''}`}
            onClick={() => setActiveTab('counselor')}
          >
            <MessageSquare size={16} /> AI Counselor
          </button>
        </nav>

        {/* Engine Status Pill */}
        <div
          className={`engine-status-pill ${health.aiConfigured ? 'online' : 'fallback'}`}
          onClick={() => setShowConfigModal(true)}
          title="Click to view AI Engine connection status and setup details"
        >
          <span className={`status-dot ${health.aiConfigured ? 'online' : 'fallback'}`} />
          <span>
            {health.aiConfigured ? `Gemini 2.5 Flash Online` : `Offline Template Mode`}
          </span>
          <Info size={14} />
        </div>
      </header>

      {/* Global Fallback Notice Banner when API Key is missing */}
      {!health.aiConfigured && !health.loading && (
        <div className="fallback-alert-banner" style={{ margin: '12px 24px 0 24px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <AlertCircle size={18} color="#d97706" />
            <span>
              <strong>Fallback Mode Active:</strong> Responses are currently generated via curated templates. To unlock dynamic Google Gemini Generative AI across all 5 features, set your API key in <code>backend/.env</code>.
            </span>
          </div>
          <button className="setup-link" onClick={() => setShowConfigModal(true)}>
            View Setup Instructions
          </button>
        </div>
      )}

      {/* ============================================================== */}
      {/* 2. Main Tab Views */}
      {/* ============================================================== */}
      <main className="app-main">
        {/* TAB 1: ROADMAP CANVAS */}
        {activeTab === 'roadmap' && (
          <div>
            {/* Control Bar */}
            <form onSubmit={handleGenerateRoadmap} className="control-panel">
              <div className="input-group" style={{ flex: '2', minWidth: '240px' }}>
                <label className="input-label">Target Career Role</label>
                <input
                  type="text"
                  className="input-field"
                  placeholder="e.g. Cloud Security Engineer, AI Engineer, Full Stack..."
                  value={roleInput}
                  onChange={(e) => setRoleInput(e.target.value)}
                />
              </div>

              <div className="input-group" style={{ minWidth: '130px' }}>
                <label className="input-label">Proficiency</label>
                <select
                  className="input-select"
                  value={levelInput}
                  onChange={(e) => setLevelInput(e.target.value)}
                >
                  <option value="Beginner">Beginner</option>
                  <option value="Intermediate">Intermediate</option>
                  <option value="Advanced">Advanced</option>
                </select>
              </div>

              <div className="input-group" style={{ minWidth: '130px' }}>
                <label className="input-label">Timeframe</label>
                <select
                  className="input-select"
                  value={timeframeInput}
                  onChange={(e) => setTimeframeInput(e.target.value)}
                >
                  <option value="3 Months">3 Months</option>
                  <option value="6 Months">6 Months</option>
                  <option value="12 Months">12 Months</option>
                </select>
              </div>

              <div style={{ alignSelf: 'flex-end' }}>
                <button type="submit" className="btn-primary" disabled={roadmapLoading}>
                  <Sparkles size={16} />
                  {roadmapLoading ? 'Synthesizing...' : 'Generate AI Roadmap'}
                </button>
              </div>
            </form>

            {/* AI Source Badge & Overview */}
            {roadmapData && (
              <div
                style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  marginBottom: '14px',
                  flexWrap: 'wrap',
                  gap: '10px',
                }}
              >
                <div>
                  <h2 style={{ margin: '0 0 4px', fontSize: '20px' }}>{roadmapData.role} Roadmap</h2>
                  <p style={{ color: 'var(--text-muted)', fontSize: '13px' }}>{roadmapData.overview}</p>
                </div>
                <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                  <span className={`ai-source-badge ${roadmapData.isAiGenerated ? 'ai-true' : 'ai-false'}`}>
                    {roadmapData.isAiGenerated ? (
                      <>
                        <Sparkles size={13} /> AI Generated: {roadmapData.modelUsed}
                      </>
                    ) : (
                      <>
                        <Layers size={13} /> Offline Template Fallback
                      </>
                    )}
                  </span>
                  <button
                    className="btn-secondary"
                    onClick={() => {
                      setAssessmentRole(roadmapData.role);
                      setActiveTab('assessment');
                    }}
                  >
                    <ShieldCheck size={14} /> Take Skill Quiz for This Role
                  </button>
                </div>
              </div>
            )}

            {/* Split View: Visual Canvas + Milestone Drawer */}
            <div className="roadmap-split-container">
              {/* Left: ReactFlow Canvas */}
              <div className="canvas-wrapper">
                <ReactFlow
                  nodes={nodes}
                  edges={edges}
                  onNodesChange={onNodesChange}
                  onEdgesChange={onEdgesChange}
                  nodeTypes={nodeTypes}
                  fitView
                >
                  <Background color="#94a3b8" gap={16} size={1} />
                  <Controls />
                </ReactFlow>
              </div>

              {/* Right: Milestone Details */}
              <div className="milestones-sidebar">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <h3 style={{ margin: 0, fontSize: '15px' }}>Milestone Objectives</h3>
                  <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                    {Object.values(completedMilestones).filter(Boolean).length} / {roadmapData?.milestones?.length || 0} Done
                  </span>
                </div>

                {roadmapData?.milestones?.map((m) => {
                  const isDone = !!completedMilestones[m.id];
                  return (
                    <div
                      key={m.id}
                      className="milestone-item-card"
                      style={{ opacity: isDone ? 0.75 : 1 }}
                    >
                      <div className="milestone-item-header">
                        <span className="milestone-badge">Step {m.stepNumber} • {m.duration}</span>
                        <button
                          onClick={() => toggleMilestoneCompleted(m.id)}
                          style={{
                            background: 'none',
                            border: 'none',
                            cursor: 'pointer',
                            color: isDone ? '#10b981' : '#94a3b8',
                          }}
                          title={isDone ? 'Mark as Incomplete' : 'Mark as Completed'}
                        >
                          <CheckCircle2 size={18} />
                        </button>
                      </div>

                      <h4 className="milestone-title">{m.title}</h4>
                      <p className="milestone-desc">{m.description}</p>

                      <div style={{ marginTop: '8px' }}>
                        <span style={{ fontSize: '11px', fontWeight: '600', color: 'var(--text-muted)' }}>
                          Skills to Acquire:
                        </span>
                        <div className="skills-pill-container">
                          {m.skillsToAcquire?.map((s, idx) => (
                            <span key={idx} className="skill-tag">{s}</span>
                          ))}
                        </div>
                      </div>

                      {m.recommendedProjects && m.recommendedProjects.length > 0 && (
                        <div style={{ marginTop: '8px', fontSize: '11px' }}>
                          <span style={{ fontWeight: '600', color: 'var(--text-muted)' }}>Key Project:</span>{' '}
                          <span>{m.recommendedProjects[0]}</span>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        )}

        {/* TAB 2: JOB DESCRIPTION ANALYZER */}
        {activeTab === 'analyzer' && (
          <div>
            <div style={{ marginBottom: '16px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <h2 style={{ margin: '0 0 4px', fontSize: '20px' }}>AI Job Description & Gap Analyzer</h2>
                <p style={{ color: 'var(--text-muted)', fontSize: '13px' }}>
                  Paste any job posting to extract required skills, responsibilities, and pinpoint your skill gaps.
                </p>
              </div>
              {analyzerData && (
                <span className={`ai-source-badge ${analyzerData.isAiGenerated ? 'ai-true' : 'ai-false'}`}>
                  {analyzerData.isAiGenerated ? `✨ AI Analyzed: ${analyzerData.modelUsed}` : `📋 Rule-Based Offline Parser`}
                </span>
              )}
            </div>

            <div className="jd-analyzer-grid">
              {/* Input Card */}
              <div className="jd-input-card">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                  <label className="input-label">Paste Job Description</label>
                  <div style={{ display: 'flex', gap: '6px' }}>
                    <button
                      type="button"
                      className="btn-secondary"
                      style={{ fontSize: '11px', padding: '3px 8px' }}
                      onClick={() => setJdText(SAMPLE_JDS.cloudSecurity)}
                    >
                      Sample: Cloud Sec JD
                    </button>
                    <button
                      type="button"
                      className="btn-secondary"
                      style={{ fontSize: '11px', padding: '3px 8px' }}
                      onClick={() => setJdText(SAMPLE_JDS.fullStack)}
                    >
                      Sample: Full Stack JD
                    </button>
                  </div>
                </div>

                <textarea
                  className="textarea-field"
                  placeholder="Paste the target job description here..."
                  value={jdText}
                  onChange={(e) => setJdText(e.target.value)}
                />

                <div style={{ marginTop: '14px' }}>
                  <label className="input-label" style={{ marginBottom: '4px', display: 'block' }}>
                    Your Current Skills (Comma-separated)
                  </label>
                  <input
                    type="text"
                    className="input-field"
                    style={{ width: '100%' }}
                    placeholder="e.g. Python, Linux, Git, Docker..."
                    value={userSkillsText}
                    onChange={(e) => setUserSkillsText(e.target.value)}
                  />
                </div>

                <div style={{ marginTop: '16px' }}>
                  <button
                    className="btn-primary"
                    style={{ width: '100%', justifyContent: 'center' }}
                    onClick={handleAnalyzeJob}
                    disabled={analyzerLoading}
                  >
                    <FileSearch size={16} />
                    {analyzerLoading ? 'Analyzing Posting with AI...' : 'Analyze Job & Extract Gaps'}
                  </button>
                </div>
              </div>

              {/* Results Dashboard */}
              <div className="jd-results-card">
                {!analyzerData ? (
                  <div style={{ textAlign: 'center', padding: '60px 20px', color: 'var(--text-muted)' }}>
                    <FileSearch size={40} style={{ opacity: 0.3, marginBottom: '10px' }} />
                    <p>Paste a job description and click "Analyze Job" to generate the skill breakdown.</p>
                  </div>
                ) : (
                  <div>
                    {/* Score Ring / Banner */}
                    <div className="score-banner">
                      <div>
                        <div style={{ fontSize: '12px', fontWeight: '600', color: 'var(--primary)' }}>
                          Candidate Match Score
                        </div>
                        <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                          {analyzerData.jobTitle} ({analyzerData.experienceLevel})
                        </div>
                      </div>
                      <div className="score-num">{analyzerData.matchScore}%</div>
                    </div>

                    {/* Skill Gaps */}
                    <div style={{ marginBottom: '16px' }}>
                      <h4 style={{ margin: '0 0 8px', fontSize: '14px' }}>Identified Skill Gaps & Action Items</h4>
                      {analyzerData.skillGaps?.map((gap, idx) => (
                        <div key={idx} className="gap-item">
                          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                            <strong style={{ fontSize: '13px' }}>{gap.skill}</strong>
                            <span className={gap.importance === 'High' ? 'importance-high' : 'importance-med'}>
                              {gap.importance} Priority
                            </span>
                          </div>
                          <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                            {gap.recommendation}
                          </div>
                        </div>
                      ))}
                    </div>

                    {/* Required Technical Skills */}
                    <div style={{ marginBottom: '16px' }}>
                      <h4 style={{ margin: '0 0 6px', fontSize: '14px' }}>Required Technical Skills</h4>
                      <div className="skills-pill-container">
                        {analyzerData.requiredTechnicalSkills?.map((s, idx) => (
                          <span key={idx} className="skill-tag" style={{ background: '#eef2ff', borderColor: '#c7d2fe' }}>
                            {s}
                          </span>
                        ))}
                      </div>
                    </div>

                    {/* Key Responsibilities */}
                    <div style={{ marginBottom: '16px' }}>
                      <h4 style={{ margin: '0 0 6px', fontSize: '14px' }}>Key Responsibilities</h4>
                      <ul style={{ margin: 0, paddingLeft: '20px', fontSize: '12px', color: 'var(--text-muted)' }}>
                        {analyzerData.keyResponsibilities?.map((r, idx) => (
                          <li key={idx} style={{ marginBottom: '4px' }}>{r}</li>
                        ))}
                      </ul>
                    </div>

                    {/* Action Plan */}
                    <div>
                      <h4 style={{ margin: '0 0 6px', fontSize: '14px' }}>Targeted Preparation Plan</h4>
                      <ul style={{ margin: 0, paddingLeft: '20px', fontSize: '12px', color: 'var(--text-muted)' }}>
                        {analyzerData.actionPlan?.map((plan, idx) => (
                          <li key={idx} style={{ marginBottom: '4px' }}>{plan}</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* TAB 3: ROLE SKILL ASSESSMENT QUIZ */}
        {activeTab === 'assessment' && (
          <div className="quiz-container">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
              <div>
                <h2 style={{ margin: '0 0 4px', fontSize: '20px' }}>Role-Specific Skill Diagnostic</h2>
                <p style={{ color: 'var(--text-muted)', fontSize: '13px' }}>
                  Test your practical competence for {assessmentRole} with dynamic scenario questions.
                </p>
              </div>
              {assessmentData && (
                <span className={`ai-source-badge ${assessmentData.isAiGenerated ? 'ai-true' : 'ai-false'}`}>
                  {assessmentData.isAiGenerated ? `✨ AI Questions: ${assessmentData.modelUsed}` : `📋 Curated Question Bank`}
                </span>
              )}
            </div>

            {/* Setup Controls */}
            <div style={{ display: 'flex', gap: '10px', marginBottom: '20px', flexWrap: 'wrap' }}>
              <input
                type="text"
                className="input-field"
                style={{ flex: 1, minWidth: '200px' }}
                placeholder="Role to assess..."
                value={assessmentRole}
                onChange={(e) => setAssessmentRole(e.target.value)}
              />
              <select
                className="input-select"
                value={assessmentDifficulty}
                onChange={(e) => setAssessmentDifficulty(e.target.value)}
              >
                <option value="Beginner">Beginner</option>
                <option value="Intermediate">Intermediate</option>
                <option value="Advanced">Advanced</option>
              </select>
              <button
                className="btn-primary"
                onClick={handleGenerateAssessment}
                disabled={assessmentLoading}
              >
                <Play size={16} />
                {assessmentLoading ? 'Synthesizing Quiz...' : 'Generate New Quiz'}
              </button>
            </div>

            {/* Questions List */}
            {assessmentData?.questions?.map((q, qIndex) => {
              const selectedOption = userAnswers[q.id];
              return (
                <div key={q.id} className="question-card">
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                    <span style={{ fontSize: '12px', fontWeight: '700', color: 'var(--primary)' }}>
                      Question {qIndex + 1} • {q.testedSkill}
                    </span>
                  </div>
                  <div style={{ fontWeight: '600', fontSize: '15px', marginBottom: '12px' }}>
                    {q.question}
                  </div>

                  {q.options.map((opt, oIndex) => {
                    let btnClass = 'option-btn';
                    if (quizSubmitted) {
                      if (oIndex === q.correctAnswerIndex) {
                        btnClass += ' correct';
                      } else if (selectedOption === oIndex) {
                        btnClass += ' wrong';
                      }
                    } else if (selectedOption === oIndex) {
                      btnClass += ' selected';
                    }

                    return (
                      <button
                        key={oIndex}
                        className={btnClass}
                        onClick={() => handleSelectOption(q.id, oIndex)}
                        disabled={quizSubmitted}
                      >
                        <span>
                          <strong>{String.fromCharCode(65 + oIndex)}.</strong> {opt}
                        </span>
                        {quizSubmitted && oIndex === q.correctAnswerIndex && (
                          <CheckCircle2 size={16} color="#10b981" />
                        )}
                      </button>
                    );
                  })}

                  {/* Show explanation after submitting */}
                  {quizSubmitted && (
                    <div className="explanation-box">
                      <strong>Explanation:</strong> {q.explanation}
                    </div>
                  )}
                </div>
              );
            })}

            {/* Submit / Results Actions */}
            {assessmentData?.questions && !quizSubmitted && (
              <div style={{ marginTop: '20px', textAlign: 'center' }}>
                <button
                  className="btn-primary"
                  style={{ padding: '12px 28px', fontSize: '15px' }}
                  onClick={handleSubmitQuiz}
                  disabled={Object.keys(userAnswers).length === 0}
                >
                  <Award size={18} /> Submit Assessment
                </button>
              </div>
            )}

            {/* Quiz Summary Modal / Card */}
            {quizSubmitted && quizScore && (
              <div
                style={{
                  background: 'var(--primary-light)',
                  border: '1px solid var(--border-color)',
                  borderRadius: '10px',
                  padding: '20px',
                  marginTop: '24px',
                  textAlign: 'center',
                }}
              >
                <Award size={36} color="var(--primary)" style={{ marginBottom: '8px' }} />
                <h3 style={{ margin: '0 0 4px', fontSize: '18px' }}>Assessment Completed</h3>
                <div style={{ fontSize: '28px', fontWeight: '800', color: 'var(--primary)', margin: '8px 0' }}>
                  {quizScore.score} / {quizScore.total} ({quizScore.percentage}%)
                </div>
                <p style={{ color: 'var(--text-muted)', fontSize: '13px', maxWidth: '500px', margin: '0 auto 16px' }}>
                  {quizScore.percentage >= 80
                    ? 'Superb demonstration of key concepts! Ready for advanced applications.'
                    : 'Good diagnostic baseline! Review the explanations above to reinforce missed skills.'}
                </p>

                <div style={{ display: 'flex', gap: '10px', justifyContent: 'center' }}>
                  <button className="btn-secondary" onClick={handleGenerateAssessment}>
                    <RotateCcw size={16} /> Retake Quiz
                  </button>
                  <button className="btn-primary" onClick={() => handleTriggerAdaptivePlan(quizScore)}>
                    <TrendingUp size={16} /> Adapt Learning Recommendations
                  </button>
                </div>
              </div>
            )}
          </div>
        )}

        {/* TAB 4: ADAPTIVE RECOMMENDATIONS */}
        {activeTab === 'adaptive' && (
          <div style={{ maxWidth: '960px', margin: '0 auto', width: '100%' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
              <div>
                <h2 style={{ margin: '0 0 4px', fontSize: '20px' }}>Adaptive Learning Recommendations</h2>
                <p style={{ color: 'var(--text-muted)', fontSize: '13px' }}>
                  Curriculum dynamically customized based on your demonstrated strengths and diagnosed gaps.
                </p>
              </div>
              {adaptiveData && (
                <span className={`ai-source-badge ${adaptiveData.isAiGenerated ? 'ai-true' : 'ai-false'}`}>
                  {adaptiveData.isAiGenerated ? `✨ AI Personalized: ${adaptiveData.modelUsed}` : `📋 Adaptive Rule Engine`}
                </span>
              )}
            </div>

            {!adaptiveData && !adaptiveLoading ? (
              <div
                style={{
                  background: 'var(--bg-card)',
                  border: '1px solid var(--border-color)',
                  borderRadius: '10px',
                  padding: '50px 20px',
                  textAlign: 'center',
                  color: 'var(--text-muted)',
                }}
              >
                <TrendingUp size={44} style={{ opacity: 0.3, marginBottom: '12px' }} />
                <h3>No Diagnostic Results Yet</h3>
                <p style={{ maxWidth: '460px', margin: '0 auto 16px', fontSize: '13px' }}>
                  Take the Skill Quiz first to allow CareerForge AI to diagnose your exact weak areas and synthesize an adaptive learning roadmap.
                </p>
                <button className="btn-primary" onClick={() => setActiveTab('assessment')}>
                  Take Skill Quiz
                </button>
              </div>
            ) : adaptiveLoading ? (
              <div style={{ textAlign: 'center', padding: '60px', color: 'var(--text-muted)' }}>
                <Sparkles size={36} color="var(--primary)" style={{ animation: 'spin 2s linear infinite' }} />
                <p style={{ marginTop: '12px' }}>Synthesizing personalized remedial plan based on your test answers...</p>
              </div>
            ) : (
              <div>
                {/* Overview Card */}
                <div
                  style={{
                    background: 'var(--bg-card)',
                    border: '1px solid var(--border-color)',
                    borderRadius: '10px',
                    padding: '20px',
                    marginBottom: '20px',
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
                    <h3 style={{ margin: 0, fontSize: '16px' }}>Diagnostic Performance Review</h3>
                    <span style={{ fontSize: '14px', fontWeight: '700', color: 'var(--primary)' }}>
                      Score: {adaptiveData.score} / {adaptiveData.totalQuestions} ({adaptiveData.percentage}%)
                    </span>
                  </div>
                  <p style={{ fontSize: '14px', color: 'var(--text-dark)', lineHeight: '1.5' }}>
                    {adaptiveData.overallEvaluation}
                  </p>
                  <div style={{ marginTop: '12px', fontSize: '13px', color: 'var(--primary)', fontWeight: '600' }}>
                    Roadmap Adjustment: {adaptiveData.nextMilestoneAdjustment}
                  </div>
                </div>

                {/* Remedial Study Plan Cards */}
                <h3 style={{ fontSize: '16px', marginBottom: '12px' }}>Targeted Remedial Action Items</h3>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', marginBottom: '24px' }}>
                  {adaptiveData.personalizedPlan?.map((plan, idx) => (
                    <div
                      key={idx}
                      style={{
                        background: 'var(--bg-card)',
                        border: '1px solid var(--border-color)',
                        borderRadius: '8px',
                        padding: '16px',
                      }}
                    >
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                        <span style={{ fontWeight: '700', fontSize: '14px' }}>{plan.topic}</span>
                        <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                          <span
                            style={{
                              fontSize: '11px',
                              fontWeight: '700',
                              padding: '2px 8px',
                              borderRadius: '4px',
                              background: plan.priority === 'Immediate' ? '#fee2e2' : '#fef3c7',
                              color: plan.priority === 'Immediate' ? '#b91c1c' : '#92400e',
                            }}
                          >
                            {plan.priority} Priority
                          </span>
                          <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                            Est. {plan.estimatedHours}
                          </span>
                        </div>
                      </div>
                      <p style={{ fontSize: '13px', color: 'var(--text-dark)', margin: '6px 0 10px' }}>
                        {plan.actionItem}
                      </p>
                      {plan.recommendedResources && (
                        <div>
                          <span style={{ fontSize: '11px', fontWeight: '600', color: 'var(--text-muted)' }}>
                            Recommended Resources:
                          </span>
                          <ul style={{ margin: '4px 0 0', paddingLeft: '18px', fontSize: '12px', color: 'var(--text-muted)' }}>
                            {plan.recommendedResources.map((res, rIdx) => (
                              <li key={rIdx}>{res}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  ))}
                </div>

                {/* Hands-on Projects designed for weak areas */}
                <h3 style={{ fontSize: '16px', marginBottom: '12px' }}>Custom Reinforcement Projects</h3>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '14px' }}>
                  {adaptiveData.handsOnProjects?.map((proj, pIdx) => (
                    <div
                      key={pIdx}
                      style={{
                        background: 'var(--bg-card)',
                        border: '1px solid var(--border-color)',
                        borderRadius: '8px',
                        padding: '16px',
                      }}
                    >
                      <h4 style={{ margin: '0 0 6px', fontSize: '14px' }}>{proj.title}</h4>
                      <p style={{ fontSize: '12px', color: 'var(--text-muted)', lineHeight: '1.4', margin: '0 0 10px' }}>
                        {proj.description}
                      </p>
                      <div className="skills-pill-container">
                        {proj.targetedSkills?.map((skill, sIdx) => (
                          <span key={sIdx} className="skill-tag">{skill}</span>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* TAB 5: AI CAREER COUNSELOR */}
        {activeTab === 'counselor' && (
          <div className="chat-window">
            <div
              style={{
                padding: '14px 20px',
                borderBottom: '1px solid var(--border-color)',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
              }}
            >
              <div>
                <h3 style={{ margin: 0, fontSize: '15px' }}>CareerForge AI Guidance Counselor</h3>
                <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                  Aware of your active role: {roleInput}
                </span>
              </div>
              <span className={`ai-source-badge ${health.aiConfigured ? 'ai-true' : 'ai-false'}`}>
                {health.aiConfigured ? `✨ Live Gemini Chat` : `📋 Offline Guidance Advisory`}
              </span>
            </div>

            {/* Chat Messages */}
            <div className="chat-messages">
              {chatMessages.map((msg, idx) => (
                <div key={idx} className={`chat-bubble ${msg.role}`}>
                  <div style={{ whiteSpace: 'pre-line' }}>{msg.content}</div>
                </div>
              ))}
              {chatLoading && (
                <div className="chat-bubble assistant" style={{ fontStyle: 'italic', color: 'var(--text-muted)' }}>
                  CareerForge Counselor is formulating guidance...
                </div>
              )}
            </div>

            {/* Quick Follow-up Prompt Chips */}
            <div
              style={{
                padding: '8px 20px',
                background: 'var(--bg-main)',
                borderTop: '1px solid var(--border-color)',
                display: 'flex',
                gap: '6px',
                overflowX: 'auto',
              }}
            >
              {suggestedQuestions.map((q, idx) => (
                <button
                  key={idx}
                  className="btn-secondary"
                  style={{ fontSize: '11px', whiteSpace: 'nowrap', borderRadius: '14px' }}
                  onClick={() => handleSendMessage(q)}
                >
                  <ChevronRight size={12} /> {q}
                </button>
              ))}
            </div>

            {/* Input Bar */}
            <form
              onSubmit={(e) => {
                e.preventDefault();
                handleSendMessage();
              }}
              className="chat-input-bar"
            >
              <input
                type="text"
                className="input-field"
                style={{ flex: 1 }}
                placeholder="Ask advice on interview prep, transitioning roles, portfolio advice..."
                value={chatInput}
                onChange={(e) => setChatInput(e.target.value)}
              />
              <button type="submit" className="btn-primary" disabled={chatLoading || !chatInput.trim()}>
                <Send size={16} /> Send
              </button>
            </form>
          </div>
        )}
      </main>

      {/* ============================================================== */}
      {/* 3. Setup & Environment Modal */}
      {/* ============================================================== */}
      {showConfigModal && (
        <div className="modal-overlay" onClick={() => setShowConfigModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
              <h3 style={{ margin: 0, fontSize: '18px' }}>AI Engine Environment Configuration</h3>
              <button
                className="btn-secondary"
                style={{ padding: '4px 8px' }}
                onClick={() => setShowConfigModal(false)}
              >
                ✕
              </button>
            </div>

            <div
              style={{
                padding: '12px 16px',
                borderRadius: '8px',
                background: health.aiConfigured ? 'rgba(16, 185, 129, 0.1)' : 'rgba(245, 158, 11, 0.1)',
                border: `1px solid ${health.aiConfigured ? 'rgba(16, 185, 129, 0.3)' : 'rgba(245, 158, 11, 0.3)'}`,
                marginBottom: '16px',
              }}
            >
              <div style={{ fontWeight: '700', fontSize: '14px', color: health.aiConfigured ? '#059669' : '#d97706' }}>
                Status: {health.aiConfigured ? 'Connected to Google Gemini' : 'Offline Template Fallback Active'}
              </div>
              <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '4px' }}>
                Active Model: <code>{health.model}</code> | Provider: Google Gemini API
              </div>
              {health.aiConfigured && (
                <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '2px' }}>
                  Masked Server Key: <code>{health.maskedKey}</code>
                </div>
              )}
            </div>

            <h4 style={{ fontSize: '14px', margin: '0 0 6px' }}>How to Configure Real Generative AI:</h4>
            <ol style={{ fontSize: '13px', color: 'var(--text-muted)', paddingLeft: '20px', margin: '0 0 16px', lineHeight: '1.6' }}>
              <li>
                Obtain your free API key from{' '}
                <a
                  href="https://aistudio.google.com/"
                  target="_blank"
                  rel="noopener noreferrer"
                  style={{ color: 'var(--primary)', fontWeight: '600' }}
                >
                  Google AI Studio <ExternalLink size={12} style={{ display: 'inline' }} />
                </a>.
              </li>
              <li>
                Open the file <code>backend/.env</code> in this project.
              </li>
              <li>
                Set your key on the server:
                <pre
                  style={{
                    background: 'var(--bg-main)',
                    padding: '8px',
                    borderRadius: '4px',
                    fontSize: '12px',
                    marginTop: '4px',
                  }}
                >
GEMINI_API_KEY=AIzaSy...
GEMINI_MODEL=gemini-2.5-flash
                </pre>
              </li>
              <li>Restart or launch the backend with <code>npm run dev:backend</code>.</li>
            </ol>

            <div style={{ background: '#f8fafc', padding: '10px 14px', borderRadius: '6px', fontSize: '12px', color: '#475569', marginBottom: '16px' }}>
              🔒 <strong>Security Architecture:</strong> Your API key is loaded server-side only through environment variables. It is never exposed in browser bundles, network requests, or frontend storage.
            </div>

            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '8px' }}>
              <button
                className="btn-secondary"
                onClick={() => {
                  checkHealth();
                }}
              >
                Re-check Connection
              </button>
              <button className="btn-primary" onClick={() => setShowConfigModal(false)}>
                Done
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}