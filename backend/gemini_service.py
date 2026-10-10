"""
Gemini Service for CareerForge AI
Integrates with the official Google GenAI SDK (google-genai) to power:
1. Personalized dynamic career roadmaps for any role
2. Job description analysis and skill gap extraction
3. Role-specific assessment questions with explanations
4. Adaptive learning recommendations based on test scores
5. Contextual AI career guidance chat

Handles:
- Missing API keys
- Rate limits (HTTP 429) & quota errors
- Timeouts & network connection errors
- JSON response validation and safe parsing
- Fallbacks with clear distinction between AI vs template
"""

import os
import json
import logging
import re
from datetime import datetime
from typing import Dict, Any, List, Optional
from concurrent.futures import ThreadPoolExecutor, TimeoutError

from google import genai
from google.genai import types
from google.genai.errors import APIError

import fallbacks

logger = logging.getLogger("CareerForge.GeminiService")

# Timeout in seconds for LLM generation
DEFAULT_TIMEOUT_SECONDS = 30

class GeminiService:
    def __init__(self):
        self._refresh_config()

    def _refresh_config(self):
        self.api_key = os.getenv("GEMINI_API_KEY", "").strip()
        self.model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash").strip()
        self.client: Optional[genai.Client] = None

        if self.is_key_configured():
            try:
                self.client = genai.Client(api_key=self.api_key)
                logger.info(f"Gemini client initialized with model '{self.model_name}'")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini Client: {e}")
                self.client = None
        else:
            logger.info("GEMINI_API_KEY is not set. Operating in offline template fallback mode.")

    def is_key_configured(self) -> bool:
        """Returns True if a non-empty API key is present."""
        return bool(self.api_key and len(self.api_key) > 5 and not self.api_key.startswith("your_"))

    def get_status(self) -> Dict[str, Any]:
        """Returns server AI status without exposing secret keys."""
        configured = self.is_key_configured()
        masked_key = ""
        if configured:
            masked_key = f"{self.api_key[:4]}...{self.api_key[-4:]}"
        return {
            "aiConfigured": configured,
            "model": self.model_name,
            "maskedKey": masked_key,
            "mode": "Live Generative AI" if configured else "Offline Template Fallback",
            "provider": "Google Gemini (Official google-genai SDK)"
        }

    def _clean_and_parse_json(self, raw_text: str) -> Optional[Dict[str, Any]]:
        """Safely parses JSON from model output, handling potential markdown fences."""
        if not raw_text:
            return None
        text = raw_text.strip()
        # Remove markdown code blocks if present
        if text.startswith("```"):
            lines = text.splitlines()
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            text = "\n".join(lines).strip()
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            # Try to extract the first balanced JSON object via regex
            match = re.search(r'(\{[\s\S]*\}|\[[\s\S]*\])', text)
            if match:
                try:
                    return json.loads(match.group(0))
                except json.JSONDecodeError:
                    pass
            logger.error(f"Failed to parse JSON from response: {raw_text[:200]}...")
            return None

    def _call_model_with_timeout(self, prompt: str, is_json: bool = True, system_instruction: str = None) -> str:
        """Invokes model with timeout and error handling."""
        if not self.client:
            raise ValueError("Gemini Client not initialized (missing API key)")

        config_args = {
            "temperature": 0.7,
        }
        if is_json:
            config_args["response_mime_type"] = "application/json"
        if system_instruction:
            config_args["system_instruction"] = system_instruction

        config = types.GenerateContentConfig(**config_args)

        def _execute():
            resp = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=config
            )
            return resp.text

        with ThreadPoolExecutor(max_workers=2) as executor:
            future = executor.submit(_execute)
            return future.result(timeout=DEFAULT_TIMEOUT_SECONDS)

    def generate_roadmap(self, role: str, level: str = "Beginner", timeframe: str = "6 Months") -> Dict[str, Any]:
        """Generates a personalized career roadmap for any user-selected job role."""
        if not self.is_key_configured():
            res = fallbacks.get_fallback_roadmap(role, level, timeframe)
            res["fallbackReason"] = "GEMINI_API_KEY environment variable is not configured on the server."
            return res

        prompt = f"""
You are a principal tech career strategist and curriculum architect.
Generate a comprehensive, highly realistic career roadmap for a user aiming to become a:
Target Role: "{role}"
Current Proficiency: "{level}"
Target Completion Timeframe: "{timeframe}"

Provide your output as a single valid JSON object with the following exact structure:
{{
  "role": "{role}",
  "level": "{level}",
  "timeframe": "{timeframe}",
  "overview": "2-3 concise sentences explaining the strategic path to break into or master this role.",
  "milestones": [
    {{
      "id": "m-1",
      "stepNumber": 1,
      "title": "Title of step (e.g. Core Foundations & Tooling)",
      "duration": "Duration (e.g. Weeks 1-4)",
      "description": "Clear explanation of what the user will achieve in this milestone.",
      "skillsToAcquire": ["Skill 1", "Skill 2", "Skill 3", "Skill 4", "Skill 5"],
      "recommendedProjects": ["Concrete portfolio project with clear requirements", "Second hands-on lab"],
      "certifications": ["Recognized industry certificate or credential"],
      "status": "in_progress"
    }}
  ]
}}

Generate between 4 and 5 progressive milestones that take the user from their current level to job-ready competence.
Be specific with real industry tools, frameworks, and modern technologies.
"""
        try:
            raw_response = self._call_model_with_timeout(
                prompt=prompt,
                is_json=True,
                system_instruction="You are an expert tech career advisor. Respond strictly with valid JSON."
            )
            data = self._clean_and_parse_json(raw_response)
            if not data or "milestones" not in data or not isinstance(data["milestones"], list):
                logger.warning("Gemini roadmap output missing required fields, using fallback.")
                res = fallbacks.get_fallback_roadmap(role, level, timeframe)
                res["fallbackReason"] = "Model generated malformed roadmap schema; safely rendered verified fallback template."
                return res

            # Build ReactFlow visual graph nodes and edges
            milestones = data.get("milestones", [])
            nodes = []
            edges = []

            # Target Goal Node (top)
            nodes.append({
                "id": "goal",
                "type": "input",
                "position": {"x": 280, "y": 40},
                "data": {
                    "label": f"🎯 Target Goal: {role.strip().title()}",
                    "stepNumber": 0,
                    "stage": "Career Goal",
                    "duration": timeframe,
                    "skills": [f"Level: {level}"]
                }
            })

            prev_id = "goal"
            for i, m in enumerate(milestones):
                step_num = m.get("stepNumber", i + 1)
                node_id = m.get("id", f"m-{step_num}")
                y_pos = 160 + (i * 125)
                x_pos = 280 if i % 2 == 0 else 320
                skills_list = m.get("skillsToAcquire", [])
                
                nodes.append({
                    "id": node_id,
                    "position": {"x": x_pos, "y": y_pos},
                    "data": {
                        "label": f"Step {step_num}: {m.get('title', 'Milestone')}",
                        "stepNumber": step_num,
                        "stage": m.get("duration", f"Phase {step_num}"),
                        "duration": m.get("duration", "4 Weeks"),
                        "skills": skills_list[:3] if isinstance(skills_list, list) else [],
                        "description": m.get("description", "")
                    }
                })
                edges.append({
                    "id": f"e-{prev_id}-{node_id}",
                    "source": prev_id,
                    "target": node_id,
                    "animated": True
                })
                prev_id = node_id

            return {
                "role": role.strip().title(),
                "level": level,
                "timeframe": timeframe,
                "overview": data.get("overview", f"AI-generated personalized roadmap for {role}."),
                "milestones": milestones,
                "nodes": nodes,
                "edges": edges,
                "isAiGenerated": True,
                "modelUsed": self.model_name,
                "generatedAt": datetime.utcnow().isoformat() + "Z"
            }

        except TimeoutError:
            logger.error("Gemini API call timed out generating roadmap.")
            res = fallbacks.get_fallback_roadmap(role, level, timeframe)
            res["fallbackReason"] = f"Gemini API request timed out after {DEFAULT_TIMEOUT_SECONDS}s. Showing offline template."
            return res
        except APIError as e:
            logger.error(f"Gemini API error generating roadmap: {e}")
            res = fallbacks.get_fallback_roadmap(role, level, timeframe)
            res["fallbackReason"] = f"Gemini API error ({getattr(e, 'code', 'error')}): {getattr(e, 'message', str(e))}"
            return res
        except Exception as e:
            logger.error(f"Unexpected error in roadmap generation: {e}")
            res = fallbacks.get_fallback_roadmap(role, level, timeframe)
            res["fallbackReason"] = f"Unexpected error contacting AI engine ({str(e)}). Fallback active."
            return res

    def analyze_job_description(self, job_description: str, user_skills: str = "") -> Dict[str, Any]:
        """Analyzes a pasted job description and extracts skills, responsibilities and skill gaps."""
        if not self.is_key_configured():
            res = fallbacks.get_fallback_job_analysis(job_description, user_skills)
            res["fallbackReason"] = "GEMINI_API_KEY environment variable is not configured on the server."
            return res

        prompt = f"""
You are an expert technical talent recruiter and engineering hiring auditor.
Analyze the following job description and evaluate it against the candidate's current skills.

Job Description:
\"\"\"
{job_description}
\"\"\"

Candidate's Current Demonstrated Skills:
\"\"\"
{user_skills if user_skills.strip() else "None provided (treat as beginner / career switcher)"}
\"\"\"

Extract and evaluate the requirements. Output a single valid JSON object with the following exact keys:
{{
  "jobTitle": "Extracted Job Title or Role Name",
  "companyType": "Inferred Industry / Company Type (e.g. Enterprise SaaS, FinTech, Early Startup)",
  "experienceLevel": "Inferred Level (e.g. Junior, Mid-Level, Senior, Lead)",
  "requiredTechnicalSkills": ["List of distinct core technical skills extracted from posting"],
  "softSkills": ["List of core soft skills, communication, and leadership traits required"],
  "keyResponsibilities": ["3 to 5 core duties and deliverables described in the posting"],
  "matchedSkills": ["Skills that candidate already possesses from their profile"],
  "skillGaps": [
    {{
      "skill": "Missing or weak skill name",
      "importance": "High" or "Medium" or "Low",
      "recommendation": "Concrete tactical advice on how to rapidly learn and demonstrate this skill."
    }}
  ],
  "matchScore": Integer between 0 and 100 representing candidate match percentage,
  "actionPlan": ["4 concrete, prioritized bullet points for candidate to bridge their gaps and prepare an application"]
}}
"""
        try:
            raw_response = self._call_model_with_timeout(
                prompt=prompt,
                is_json=True,
                system_instruction="You are a senior technical recruiter and talent analyst. Respond strictly in valid JSON."
            )
            data = self._clean_and_parse_json(raw_response)
            if not data or "requiredTechnicalSkills" not in data:
                logger.warning("Gemini JD analysis missing required fields, using fallback.")
                res = fallbacks.get_fallback_job_analysis(job_description, user_skills)
                res["fallbackReason"] = "Model response structure incomplete; rendered rule-based analysis."
                return res

            return {
                "jobTitle": data.get("jobTitle", "Target Role"),
                "companyType": data.get("companyType", "Technology"),
                "experienceLevel": data.get("experienceLevel", "Mid-Level"),
                "requiredTechnicalSkills": data.get("requiredTechnicalSkills", []),
                "softSkills": data.get("softSkills", []),
                "keyResponsibilities": data.get("keyResponsibilities", []),
                "userCurrentSkills": [s.strip() for s in user_skills.split(",") if s.strip()] if user_skills else ["None specified"],
                "matchedSkills": data.get("matchedSkills", []),
                "skillGaps": data.get("skillGaps", []),
                "matchScore": data.get("matchScore", 50),
                "actionPlan": data.get("actionPlan", []),
                "isAiGenerated": True,
                "modelUsed": self.model_name,
                "generatedAt": datetime.utcnow().isoformat() + "Z"
            }

        except TimeoutError:
            res = fallbacks.get_fallback_job_analysis(job_description, user_skills)
            res["fallbackReason"] = "Gemini API timed out during JD analysis. Showing offline heuristic analysis."
            return res
        except APIError as e:
            res = fallbacks.get_fallback_job_analysis(job_description, user_skills)
            res["fallbackReason"] = f"Gemini API error ({getattr(e, 'code', 'error')}): {getattr(e, 'message', str(e))}"
            return res
        except Exception as e:
            res = fallbacks.get_fallback_job_analysis(job_description, user_skills)
            res["fallbackReason"] = f"Unexpected error contacting AI engine ({str(e)})."
            return res

    def generate_assessment(self, role: str, difficulty: str = "Beginner", num_questions: int = 5, focus_skill: str = "") -> Dict[str, Any]:
        """Generates role-specific assessment questions with answers and explanations."""
        if not self.is_key_configured():
            res = fallbacks.get_fallback_assessment(role, difficulty, num_questions)
            res["fallbackReason"] = "GEMINI_API_KEY environment variable is not configured on the server."
            return res

        focus_clause = f"Focus particularly on the skill/subdomain: '{focus_skill}'." if focus_skill.strip() else ""

        prompt = f"""
You are a senior technical interviewer creating a rigorous, fair technical diagnostic quiz.
Target Role: "{role}"
Difficulty Level: "{difficulty}"
Number of Questions: {num_questions}
{focus_clause}

Generate {num_questions} high quality, practical, conceptual or scenario-based multiple choice questions.
For each question, provide 4 plausible options, specify the exact 0-indexed correct answer, a thorough technical explanation, and the specific skill being tested.

Output a single valid JSON object with the following exact structure:
{{
  "role": "{role}",
  "difficulty": "{difficulty}",
  "questions": [
    {{
      "id": 1,
      "question": "The question text posing a realistic technical problem or concept scenario",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "correctAnswerIndex": 0,
      "explanation": "Detailed technical explanation explaining why the correct choice is accurate and why the other choices are incorrect.",
      "testedSkill": "Specific skill tag (e.g. Docker Container Isolation, VPC Peering, Vector Indexing)"
    }}
  ]
}}
"""
        try:
            raw_response = self._call_model_with_timeout(
                prompt=prompt,
                is_json=True,
                system_instruction="You are a senior technical interviewer. Respond strictly with valid JSON."
            )
            data = self._clean_and_parse_json(raw_response)
            if not data or "questions" not in data or not isinstance(data["questions"], list) or len(data["questions"]) == 0:
                res = fallbacks.get_fallback_assessment(role, difficulty, num_questions)
                res["fallbackReason"] = "AI response missing valid questions array; loaded curated question bank."
                return res

            return {
                "role": role.strip().title(),
                "difficulty": difficulty,
                "questions": data.get("questions", []),
                "isAiGenerated": True,
                "modelUsed": self.model_name,
                "generatedAt": datetime.utcnow().isoformat() + "Z"
            }

        except TimeoutError:
            res = fallbacks.get_fallback_assessment(role, difficulty, num_questions)
            res["fallbackReason"] = "Gemini API timed out generating assessment. Showing curated assessment bank."
            return res
        except APIError as e:
            res = fallbacks.get_fallback_assessment(role, difficulty, num_questions)
            res["fallbackReason"] = f"Gemini API error ({getattr(e, 'code', 'error')}): {getattr(e, 'message', str(e))}"
            return res
        except Exception as e:
            res = fallbacks.get_fallback_assessment(role, difficulty, num_questions)
            res["fallbackReason"] = f"Unexpected error contacting AI engine ({str(e)})."
            return res

    def adapt_recommendations(
        self,
        role: str,
        score: int,
        total_questions: int,
        correct_skills: List[str],
        missed_skills: List[str],
        detailed_results: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Adapts learning recommendations based on assessment results and demonstrated skills."""
        if not self.is_key_configured():
            res = fallbacks.get_fallback_adapted_recommendations(role, score, total_questions, correct_skills, missed_skills)
            res["fallbackReason"] = "GEMINI_API_KEY environment variable is not configured on the server."
            return res

        percentage = int((score / max(total_questions, 1)) * 100)

        prompt = f"""
You are an adaptive learning specialist and engineering mentor.
A candidate for the role of "{role}" just completed a technical skills assessment.
Performance Summary:
- Score: {score} out of {total_questions} ({percentage}%)
- Demonstrably Strong Skills: {', '.join(correct_skills) if correct_skills else 'None demonstrated yet'}
- Identified Weak / Missed Skills: {', '.join(missed_skills) if missed_skills else 'None missed (Perfect score)'}

Analyze these diagnostic results and generate an adaptive, high-impact remedial learning plan specifically tailored to plug their diagnosed gaps.

Output a single valid JSON object with the following exact keys:
{{
  "role": "{role}",
  "score": {score},
  "totalQuestions": {total_questions},
  "percentage": {percentage},
  "overallEvaluation": "Empathetic, clear 2-sentence assessment of their current readiness level.",
  "strengths": ["List of confirmed competencies"],
  "weaknesses": ["List of specific diagnosed knowledge gaps"],
  "personalizedPlan": [
    {{
      "priority": "Immediate" or "High" or "Medium",
      "topic": "Name of topic needing remediation",
      "actionItem": "Specific practical task or deep dive to master this topic",
      "estimatedHours": "e.g. 6-8 hours",
      "recommendedResources": ["2-3 specific documentation sites, RFCs, books, or sandbox platforms"]
    }}
  ],
  "handsOnProjects": [
    {{
      "title": "Bespoke project designed to force application of weak skills",
      "description": "2 sentences describing what they should build and test",
      "targetedSkills": ["Skill 1", "Skill 2"]
    }}
  ],
  "nextMilestoneAdjustment": "Specific recommendation on how to adjust their career roadmap in light of these assessment results."
}}
"""
        try:
            raw_response = self._call_model_with_timeout(
                prompt=prompt,
                is_json=True,
                system_instruction="You are an adaptive technical education coach. Respond strictly in valid JSON."
            )
            data = self._clean_and_parse_json(raw_response)
            if not data or "personalizedPlan" not in data:
                res = fallbacks.get_fallback_adapted_recommendations(role, score, total_questions, correct_skills, missed_skills)
                res["fallbackReason"] = "AI response missing plan details; rendered rule-based adaptive plan."
                return res

            return {
                "role": role.strip().title(),
                "score": score,
                "totalQuestions": total_questions,
                "percentage": percentage,
                "overallEvaluation": data.get("overallEvaluation", "Diagnostic completed."),
                "strengths": data.get("strengths", correct_skills),
                "weaknesses": data.get("weaknesses", missed_skills),
                "personalizedPlan": data.get("personalizedPlan", []),
                "handsOnProjects": data.get("handsOnProjects", []),
                "nextMilestoneAdjustment": data.get("nextMilestoneAdjustment", "Continue following roadmap."),
                "isAiGenerated": True,
                "modelUsed": self.model_name,
                "generatedAt": datetime.utcnow().isoformat() + "Z"
            }

        except TimeoutError:
            res = fallbacks.get_fallback_adapted_recommendations(role, score, total_questions, correct_skills, missed_skills)
            res["fallbackReason"] = "Gemini API timed out during recommendation adaptation."
            return res
        except APIError as e:
            res = fallbacks.get_fallback_adapted_recommendations(role, score, total_questions, correct_skills, missed_skills)
            res["fallbackReason"] = f"Gemini API error ({getattr(e, 'code', 'error')}): {getattr(e, 'message', str(e))}"
            return res
        except Exception as e:
            res = fallbacks.get_fallback_adapted_recommendations(role, score, total_questions, correct_skills, missed_skills)
            res["fallbackReason"] = f"Unexpected error contacting AI engine ({str(e)})."
            return res

    def chat_guidance(self, messages: List[Dict[str, str]], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Provides contextual AI career counseling."""
        if not self.is_key_configured():
            res = fallbacks.get_fallback_guidance(messages, context)
            res["fallbackReason"] = "GEMINI_API_KEY environment variable is not configured on the server."
            return res

        context_str = json.dumps(context or {}, indent=2)
        history_str = "\n".join([f"{m.get('role', 'user').upper()}: {m.get('content', '')}" for m in messages])

        prompt = f"""
You are an elite, empathetic, and pragmatic AI career counselor at CareerForge AI.
You help engineers, analysts, and aspiring tech professionals navigate career pivots, interview preparation, portfolio building, and skill progression.

Context of user's current session:
{context_str}

Conversation History:
{history_str}

Provide a thoughtful, structured, and immediately actionable response.
Include:
- Clear direct answer to the user's latest query
- Tactical recommendations or step-by-step guidance
- Common pitfalls to avoid
- 3 suggested follow-up questions the user might want to ask next

Output a single valid JSON object with:
{{
  "reply": "Your full response formatted in rich markdown with clear headings, bullet points, and code/design examples if applicable.",
  "suggestedNextQuestions": ["Question 1", "Question 2", "Question 3"]
}}
"""
        try:
            raw_response = self._call_model_with_timeout(
                prompt=prompt,
                is_json=True,
                system_instruction="You are an elite career counselor. Respond strictly in valid JSON."
            )
            data = self._clean_and_parse_json(raw_response)
            if not data or "reply" not in data:
                res = fallbacks.get_fallback_guidance(messages, context)
                res["fallbackReason"] = "AI counselor response format invalid; showing fallback advisory."
                return res

            return {
                "reply": data.get("reply", ""),
                "suggestedNextQuestions": data.get("suggestedNextQuestions", []),
                "isAiGenerated": True,
                "modelUsed": self.model_name,
                "generatedAt": datetime.utcnow().isoformat() + "Z"
            }

        except TimeoutError:
            res = fallbacks.get_fallback_guidance(messages, context)
            res["fallbackReason"] = "Gemini API timed out during career guidance chat."
            return res
        except APIError as e:
            res = fallbacks.get_fallback_guidance(messages, context)
            res["fallbackReason"] = f"Gemini API error ({getattr(e, 'code', 'error')}): {getattr(e, 'message', str(e))}"
            return res
        except Exception as e:
            res = fallbacks.get_fallback_guidance(messages, context)
            res["fallbackReason"] = f"Unexpected error contacting AI engine ({str(e)})."
            return res
