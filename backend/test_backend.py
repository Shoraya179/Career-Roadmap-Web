"""
Test suite for CareerForge AI Backend API
Tests all 5 endpoints in fallback mode and verifies schemas, error isolation, and key protection.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def test_health_endpoint():
    """Verify health endpoint does not leak secret API key and returns status."""
    res = client.get("/api/health")
    assert res.status_code == 200, f"Health check failed: {res.text}"
    data = res.json()
    assert data["status"] == "healthy"
    assert "service" in data
    assert "aiConfigured" in data
    # Ensure raw secret is not in data
    assert "GEMINI_API_KEY" not in data
    print("[PASS] test_health_endpoint passed")

def test_roadmap_endpoint():
    """Verify roadmap generation returns structured nodes, edges, milestones."""
    payload = {
        "role": "Cloud Security Engineer",
        "level": "Beginner",
        "timeframe": "6 Months"
    }
    res = client.post("/api/roadmap/generate", json=payload)
    assert res.status_code == 200, f"Roadmap failed: {res.text}"
    data = res.json()
    assert "milestones" in data
    assert len(data["milestones"]) >= 3
    assert "nodes" in data
    assert len(data["nodes"]) >= 4
    assert "edges" in data
    assert "isAiGenerated" in data
    # Verify nodes have valid coordinates
    for node in data["nodes"]:
        assert "id" in node
        assert "position" in node
        assert "x" in node["position"]
        assert "y" in node["position"]
        assert "data" in node
    print("[PASS] test_roadmap_endpoint passed (Milestones count:", len(data["milestones"]), ")")

def test_job_analysis_endpoint():
    """Verify job description analysis extracts skills, gaps, and responsibilities."""
    jd = """
    We are looking for a Senior DevOps Engineer with 3+ years experience.
    Responsibilities:
    - Build and maintain scalable Kubernetes clusters and CI/CD pipelines using GitHub Actions.
    - Implement infrastructure as code using Terraform and Ansible.
    - Ensure cloud infrastructure security following CIS benchmarks and SOC2 compliance.
    Requirements:
    - Strong proficiency in Docker, Kubernetes, Linux bash scripting.
    - Experience with AWS (EC2, EKS, IAM, VPC).
    - Excellent communication and collaboration skills.
    """
    payload = {
        "jobDescription": jd,
        "userSkills": "Linux bash scripting, Docker"
    }
    res = client.post("/api/job/analyze", json=payload)
    assert res.status_code == 200, f"Job analysis failed: {res.text}"
    data = res.json()
    assert "requiredTechnicalSkills" in data
    assert len(data["requiredTechnicalSkills"]) > 0
    assert "keyResponsibilities" in data
    assert "skillGaps" in data
    assert "matchScore" in data
    assert "isAiGenerated" in data
    print("[PASS] test_job_analysis_endpoint passed (Gaps count:", len(data["skillGaps"]), ")")

def test_assessment_endpoint():
    """Verify role assessment generates authentic questions with answers and explanations."""
    payload = {
        "role": "DevOps Engineer",
        "difficulty": "Beginner",
        "numQuestions": 5
    }
    res = client.post("/api/assessment/generate", json=payload)
    assert res.status_code == 200, f"Assessment failed: {res.text}"
    data = res.json()
    assert "questions" in data
    assert len(data["questions"]) == 5
    for q in data["questions"]:
        assert "question" in q
        assert "options" in q
        assert len(q["options"]) == 4
        assert "correctAnswerIndex" in q
        assert 0 <= q["correctAnswerIndex"] < 4
        assert "explanation" in q
        assert len(q["explanation"]) > 10
        assert "testedSkill" in q
    assert "isAiGenerated" in data
    print("[PASS] test_assessment_endpoint passed (5 questions validated)")

def test_adaptive_recommendations_endpoint():
    """Verify adaptive learning adapts based on assessment score and missed skills."""
    payload = {
        "role": "DevOps Engineer",
        "score": 3,
        "totalQuestions": 5,
        "correctSkills": ["Docker", "Linux Administration"],
        "missedSkills": ["Kubernetes & Helm", "Infrastructure as Code (Terraform)"],
        "detailedResults": []
    }
    res = client.post("/api/assessment/adapt", json=payload)
    assert res.status_code == 200, f"Adaptive recommendations failed: {res.text}"
    data = res.json()
    assert "overallEvaluation" in data
    assert "personalizedPlan" in data
    assert len(data["personalizedPlan"]) > 0
    assert "handsOnProjects" in data
    assert "nextMilestoneAdjustment" in data
    assert "isAiGenerated" in data
    print("[PASS] test_adaptive_recommendations_endpoint passed")

def test_guidance_chat_endpoint():
    """Verify contextual career guidance chat."""
    payload = {
        "messages": [
            {"role": "user", "content": "How should I prepare for a junior DevOps role with no prior production experience?"}
        ],
        "context": {
            "currentRole": "DevOps Engineer",
            "assessmentScore": 60
        }
    }
    res = client.post("/api/guidance/chat", json=payload)
    assert res.status_code == 200, f"Guidance chat failed: {res.text}"
    data = res.json()
    assert "reply" in data
    assert len(data["reply"]) > 20
    assert "suggestedNextQuestions" in data
    assert "isAiGenerated" in data
    print("[PASS] test_guidance_chat_endpoint passed")

def test_error_resilience_and_graceful_fallback():
    """Verify that an invalid API key or network failure triggers graceful fallback without crashing."""
    from gemini_service import GeminiService
    service = GeminiService()
    # Configure an intentionally invalid key
    service.api_key = "AIzaSy_INVALID_KEY_FOR_TESTING_PURPOSES"
    try:
        from google import genai
        service.client = genai.Client(api_key=service.api_key)
    except Exception:
        pass
    
    # Request should NOT throw an uncaught exception; it must return a fallback response
    res = service.generate_roadmap("Quantum Computing Engineer", "Beginner", "6 Months")
    assert res is not None
    assert res["isAiGenerated"] is False
    assert "fallbackNotice" in res or "fallbackReason" in res
    assert len(res["milestones"]) > 0
    print("[PASS] test_error_resilience_and_graceful_fallback passed (Fallback safely activated)")

if __name__ == "__main__":
    print("\n--- Running CareerForge AI Backend Test Suite ---")
    test_health_endpoint()
    test_roadmap_endpoint()
    test_job_analysis_endpoint()
    test_assessment_endpoint()
    test_adaptive_recommendations_endpoint()
    test_guidance_chat_endpoint()
    test_error_resilience_and_graceful_fallback()
    print("--- ALL BACKEND TESTS PASSED SUCCESSFULLY! ---\n")
