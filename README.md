# CareerForge AI - Real Generative AI Career Navigator

CareerForge AI is an intelligent career acceleration platform powered by **Google Gemini Generative AI** (via the official `google-genai` SDK). It moves beyond static templates by synthesizing personalized roadmaps, auditing job postings, generating technical diagnostic assessments, adapting learning paths, and providing contextual career mentorship.

---

## 🌟 Key Capabilities

1. **Dynamic Career Roadmaps for Any Role**
   - Synthesizes bespoke multi-stage career progression paths for any job title (e.g. *Cloud Security Engineer*, *Full Stack Developer*, *AI Engineer*, *Bioinformatics Researcher*).
   - Renders an interactive visual node-and-edge graph canvas via `@xyflow/react` alongside structured milestone checklists, recommended portfolio projects, and certifications.

2. **Job Description & Skill Gap Analyzer**
   - Parses pasted job postings to extract core technical competencies, soft skills, and key responsibilities.
   - Compares requirements against candidate skills to calculate a Match Score and diagnose specific skill gaps with prioritized recommendations.

3. **Role-Specific Skill Diagnostic & Interactive Quiz**
   - Synthesizes realistic technical multiple-choice scenario questions tailored to any role and difficulty level.
   - Interactive quiz interface with immediate feedback, answer verification, and in-depth conceptual explanations.

4. **Adaptive Learning Recommendations**
   - Dynamically adapts remedial study plans and hands-on portfolio projects based on the user's diagnosed weak areas and test score.
   - Recommends concrete documentation, RFCs, and roadmap adjustments.

5. **Contextual AI Career Counselor**
   - Multi-turn conversational counselor aware of your currently active role, roadmap objectives, assessment score, and identified gaps.
   - Offers actionable portfolio advice, behavioral/technical interview strategies, and interactive follow-up prompts.

---

## 🔒 Security & Architecture Principles

- **Server-Side API Key Isolation**: The `GEMINI_API_KEY` is loaded strictly on the backend via environment variables. It is never embedded in client bundles or exposed to frontend code.
- **Official Google GenAI SDK**: Integrates using `google.genai` (`google-genai>=2.20.0`) with structured JSON schema outputs (`response_mime_type="application/json"`).
- **Resilient Fallback Mode**: If the API key is not yet configured, rate limits (HTTP 429) occur, or the network is offline, CareerForge AI gracefully serves curated offline templates without crashing.
- **Truthful Labeling**: Every response is clearly badged as either:
  - `✨ AI-Generated (Gemini 2.5 Flash)`
  - `📋 Offline Fallback Template`
  Hardcoded content is never misleadingly presented as AI-generated.

---

## ⚙️ Environment Variables

Create or edit `backend/.env` (a template is provided in `backend/.env.example`):

| Variable | Description | Default | Required for AI |
| :--- | :--- | :--- | :--- |
| `GEMINI_API_KEY` | Google Gemini API key from [Google AI Studio](https://aistudio.google.com/) | *(Empty)* | **Yes** (Runs in fallback mode if omitted) |
| `GEMINI_MODEL` | Gemini model to use (`gemini-2.5-flash`, `gemini-1.5-flash`, etc.) | `gemini-2.5-flash` | No |
| `PORT` | FastAPI backend server port | `8000` | No |

---

## 🚀 Quickstart & Setup Guide

### 1. Prerequisites
- **Python**: 3.10+ (`python` / `py`)
- **Node.js**: 18+ and `npm`

### 2. Backend Setup
```bash
# Navigate to project root
cd Career-Roadmap-Web

# Install Python backend dependencies
py -m pip install -r backend/requirements.txt

# (Optional) Add your Gemini API key to backend/.env
# GEMINI_API_KEY=your_actual_key_here

# Start the FastAPI backend server
npm run dev:backend
# Or directly: py backend/app.py
```
*The backend runs on `http://127.0.0.1:8000` with interactive API docs at `http://127.0.0.1:8000/docs`.*

### 3. Frontend Setup
```bash
# Install frontend packages (React 19, @xyflow/react, Lucide, Vite)
npm install

# Start Vite development server (proxies /api to localhost:8000)
npm run dev
```
*Open `http://localhost:5173` in your browser.*

### 4. Running Backend Tests
```bash
# Run the automated backend test suite
npm run test:backend
# Or directly: py backend/test_backend.py
```

The test suite validates:
- API key masking in health checks
- Dynamic roadmap generation & node formatting
- Job description skill gap extraction
- 5-question assessment quizzes with explanations
- Adaptive learning recommendation generation
- Contextual career counselor chat
- Error resilience and safe fallback activation under invalid credentials
