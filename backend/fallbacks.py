"""
Fallback templates and rule-based fallback generators for CareerForge AI.
These are strictly used ONLY when:
1. GEMINI_API_KEY is not set or empty.
2. Gemini API hits rate limits (429) or timeouts.
3. Network connection to Gemini API fails.

All fallback responses are explicitly flagged with:
- isAiGenerated: False
- fallbackNotice: Human-readable explanation of why fallback was used
"""

from typing import Dict, List, Any
import re
from datetime import datetime

def get_fallback_roadmap(role: str, level: str = "Beginner", timeframe: str = "6 Months") -> Dict[str, Any]:
    """Generates a structured career roadmap template when AI is unavailable."""
    role_normalized = role.strip().lower()
    
    # Pre-crafted high quality domain milestones
    if "cloud" in role_normalized or "security" in role_normalized:
        milestones = [
            {
                "id": "m-1",
                "stepNumber": 1,
                "title": "Core Foundations: Linux, Networking & Security Baselines",
                "duration": "Weeks 1-4",
                "description": "Master command-line proficiency, TCP/IP, OSI model, subnetting, DNS, firewall mechanics, and basic cryptographic primitives.",
                "skillsToAcquire": ["Linux Administration", "Bash Scripting", "TCP/IP & Routing", "Wireshark", "PKI & SSL/TLS"],
                "recommendedProjects": ["Set up a hardened Linux bastion server with key-based SSH and iptables firewall rules.", "Network packet capture and protocol analysis lab."],
                "certifications": ["CompTIA Security+", "Linux Professional Institute LPIC-1"],
                "status": "in_progress"
            },
            {
                "id": "m-2",
                "stepNumber": 2,
                "title": "Cloud Architecture & Identity (AWS / Azure / GCP)",
                "duration": "Weeks 5-10",
                "description": "Understand cloud service models (IaaS/PaaS/SaaS), IAM least-privilege policies, VPC peering, and secure cloud networking.",
                "skillsToAcquire": ["AWS IAM / Azure Entra ID", "VPC & Security Groups", "CloudTrail & GuardDuty", "S3 Bucket Hardening"],
                "recommendedProjects": ["Deploy a 3-tier high-availability web architecture inside an isolated private subnet with NAT Gateway.", "Automate IAM policy auditing with Python."],
                "certifications": ["AWS Certified Solutions Architect Associate", "Microsoft Azure Fundamentals AZ-900"],
                "status": "not_started"
            },
            {
                "id": "m-3",
                "stepNumber": 3,
                "title": "DevSecOps & Infrastructure as Code (IaC)",
                "duration": "Weeks 11-16",
                "description": "Embed security into CI/CD pipelines, scan code for vulnerabilities, and define declarative infrastructure with Terraform.",
                "skillsToAcquire": ["Terraform", "Docker & Kubernetes Basics", "GitHub Actions CI/CD", "Trivy / Snyk Vulnerability Scanning"],
                "recommendedProjects": ["Write Terraform scripts for a zero-trust multi-region VPC with automated tfsec checks in CI/CD pipeline.", "Container vulnerability scanner webhook."],
                "certifications": ["HashiCorp Certified: Terraform Associate"],
                "status": "not_started"
            },
            {
                "id": "m-4",
                "stepNumber": 4,
                "title": "Cloud Incident Response & Security Automation",
                "duration": "Weeks 17-24",
                "description": "Implement SIEM logging, threat detection alerts, and automated remediation workflows using Serverless functions.",
                "skillsToAcquire": ["AWS Security Hub", "Splunk / ELK Stack", "Python for Automation (Boto3)", "CIS Benchmarks"],
                "recommendedProjects": ["Build an automated AWS Lambda function that quarantines EC2 instances and alerts Slack upon detection of malicious outbound traffic.", "CIS Benchmark audit script."],
                "certifications": ["AWS Certified Security - Specialty", "Certified Cloud Security Professional (CCSP)"],
                "status": "not_started"
            }
        ]
    elif "ai" in role_normalized or "machine learning" in role_normalized or "data science" in role_normalized:
        milestones = [
            {
                "id": "m-1",
                "stepNumber": 1,
                "title": "Mathematical Foundations & Python Mastery",
                "duration": "Weeks 1-4",
                "description": "Master linear algebra, multivariable calculus, probability, statistics, and advanced vectorized Python using NumPy and Pandas.",
                "skillsToAcquire": ["Python 3.x", "NumPy & Pandas", "Linear Algebra", "Hypothesis Testing", "Data Cleaning"],
                "recommendedProjects": ["Exploratory Data Analysis and statistical significance dashboard on real-world financial or medical datasets."],
                "certifications": ["DeepLearning.AI Mathematics for Machine Learning"],
                "status": "in_progress"
            },
            {
                "id": "m-2",
                "stepNumber": 2,
                "title": "Classical Machine Learning & Feature Engineering",
                "duration": "Weeks 5-10",
                "description": "Implement regression, decision trees, ensemble models (RandomForest, XGBoost), regularization, and cross-validation techniques.",
                "skillsToAcquire": ["Scikit-Learn", "XGBoost", "Feature Engineering", "Model Evaluation Metrics (ROC-AUC, F1-Score)"],
                "recommendedProjects": ["End-to-end customer churn prediction pipeline with cross-validation and hyperparameter tuning."],
                "certifications": ["Kaggle Competitions / Scikit-Learn Certification"],
                "status": "not_started"
            },
            {
                "id": "m-3",
                "stepNumber": 3,
                "title": "Deep Learning & Transformer Architectures",
                "duration": "Weeks 11-18",
                "description": "Build neural networks with PyTorch, delve into CNNs, RNNs/LSTMs, Self-Attention mechanisms, and Hugging Face Transformers.",
                "skillsToAcquire": ["PyTorch", "Hugging Face Transformers", "Attention Mechanisms", "Fine-Tuning LLMs (LoRA/QLoRA)", "Vector Databases"],
                "recommendedProjects": ["Build a Retrieval-Augmented Generation (RAG) system with ChromaDB and a locally quantized Llama-3 model."],
                "certifications": ["DeepLearning.AI Deep Learning Specialization"],
                "status": "not_started"
            },
            {
                "id": "m-4",
                "stepNumber": 4,
                "title": "MLOps, Serving & Production Deployment",
                "duration": "Weeks 19-24",
                "description": "Package models into low-latency REST/gRPC microservices, monitor model drift, and orchestrate ML pipelines.",
                "skillsToAcquire": ["FastAPI", "Docker", "MLflow", "Model Monitoring & Evident Drift", "Triton / ONNX Runtime"],
                "recommendedProjects": ["Production-ready FastAPI inference engine with batch prediction, Prometheus metrics, and automated canary deployment."],
                "certifications": ["AWS Certified Machine Learning - Specialty"],
                "status": "not_started"
            }
        ]
    elif "frontend" in role_normalized or "full stack" in role_normalized or "web" in role_normalized or "developer" in role_normalized:
        milestones = [
            {
                "id": "m-1",
                "stepNumber": 1,
                "title": "Modern JavaScript & Responsive Web Architecture",
                "duration": "Weeks 1-4",
                "description": "Deep understanding of ES6+, Async/Await, DOM lifecycle, CSS Grid/Flexbox, and accessible web standards (WCAG).",
                "skillsToAcquire": ["JavaScript (ESNext)", "TypeScript Basics", "Semantic HTML5", "Tailwind CSS / Modern CSS", "Git Workflows"],
                "recommendedProjects": ["Interactive component library and stateful responsive web app with pure Vanilla JS / TypeScript."],
                "certifications": ["Meta Front-End Developer Certificate"],
                "status": "in_progress"
            },
            {
                "id": "m-2",
                "stepNumber": 2,
                "title": "Component Framework Mastery (React & Next.js)",
                "duration": "Weeks 5-10",
                "description": "Master React hooks, state management patterns, Server-Side Rendering (SSR), and performance profiling.",
                "skillsToAcquire": ["React 19", "Next.js / App Router", "Zustand / Redux Toolkit", "TanStack Query", "REST & GraphQL"],
                "recommendedProjects": ["Collaborative real-time board or dashboard with optimistic UI updates and server caching."],
                "certifications": ["Meta Advanced React Certificate"],
                "status": "not_started"
            },
            {
                "id": "m-3",
                "stepNumber": 3,
                "title": "Backend Engineering & API Design",
                "duration": "Weeks 11-16",
                "description": "Design relational and NoSQL databases, build robust REST/GraphQL APIs, handle authentication, and implement caching.",
                "skillsToAcquire": ["Node.js / Express / FastAPI", "PostgreSQL & Prisma / SQLAlchemy", "Redis Caching", "JWT & OAuth2"],
                "recommendedProjects": ["Full-stack multi-tenant SaaS application with database indexing, Stripe checkout, and webhook handlers."],
                "certifications": ["PostgreSQL Associate Certification"],
                "status": "not_started"
            },
            {
                "id": "m-4",
                "stepNumber": 4,
                "title": "Production Deployment, Testing & Performance",
                "duration": "Weeks 17-24",
                "description": "Write automated end-to-end and unit tests, configure CI/CD pipelines, optimize Core Web Vitals, and deploy to cloud.",
                "skillsToAcquire": ["Vitest / Jest", "Playwright / Cypress", "Docker", "CI/CD (GitHub Actions)", "Edge Deployment (Vercel/AWS)"],
                "recommendedProjects": ["Deploy a containerized full-stack application with automated E2E testing suite and 95+ Lighthouse score."],
                "certifications": ["AWS Certified Developer Associate"],
                "status": "not_started"
            }
        ]
    else:
        # Generic role synthesized template
        title_cap = role.strip().title()
        milestones = [
            {
                "id": "m-1",
                "stepNumber": 1,
                "title": f"Core Foundations of {title_cap}",
                "duration": "Month 1-2",
                "description": f"Master the baseline principles, foundational tools, industry terminologies, and essential workflows for {title_cap}.",
                "skillsToAcquire": [f"{title_cap} Fundamentals", "Core Domain Concepts", "Standard Industry Tooling", "Problem Decomposition"],
                "recommendedProjects": [f"Create a comprehensive starter repository solving fundamental {title_cap} problem sets."],
                "certifications": [f"Foundational {title_cap} Professional Credential"],
                "status": "in_progress"
            },
            {
                "id": "m-2",
                "stepNumber": 2,
                "title": f"Intermediate Application & Practical Tooling",
                "duration": "Month 3-4",
                "description": f"Deepen technical capabilities, work with standard frameworks, and apply industry best practices in real-world scenarios.",
                "skillsToAcquire": ["Workflow Optimization", "Data Handling", "System Architecture", "Collaboration & Version Control"],
                "recommendedProjects": [f"Build an end-to-end prototype addressing an authentic challenge in the {title_cap} domain."],
                "certifications": [f"Intermediate {title_cap} Practitioner Certification"],
                "status": "not_started"
            },
            {
                "id": "m-3",
                "stepNumber": 3,
                "title": f"Advanced Problem Solving & Specialized Skills",
                "duration": "Month 5-6",
                "description": f"Tackle edge cases, scalability, compliance, cross-disciplinary integration, and performance optimization for {title_cap}.",
                "skillsToAcquire": ["Scalability & Efficiency", "Security & Reliability", "Advanced Diagnostics", "Metrics & Monitoring"],
                "recommendedProjects": [f"Publish a production-grade capstone project showcasing complex features for {title_cap}."],
                "certifications": [f"Senior / Specialist {title_cap} Certification"],
                "status": "not_started"
            },
            {
                "id": "m-4",
                "stepNumber": 4,
                "title": "Portfolio Polishing, Interview Prep & Industry Entry",
                "duration": "Month 6+",
                "description": f"Prepare behavioral and technical interview scenarios, polish public portfolio, and engage in open-source or commercial projects.",
                "skillsToAcquire": ["Technical Communication", "System Design Reviews", "Portfolio Presentation", "Collaborative Code Reviews"],
                "recommendedProjects": [f"Document and open-source your capstone with architecture diagrams, benchmarks, and interactive live demo."],
                "certifications": ["Industry Professional Showcase Credential"],
                "status": "not_started"
            }
        ]

    # Convert milestones into ReactFlow node and edge structures
    nodes = []
    edges = []
    
    # Target goal node at top
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
        node_id = m["id"]
        y_pos = 160 + (i * 120)
        # alternate slight x offset for nice flow diagram
        x_pos = 280 if i % 2 == 0 else 320
        nodes.append({
            "id": node_id,
            "position": {"x": x_pos, "y": y_pos},
            "data": {
                "label": f"Step {m['stepNumber']}: {m['title']}",
                "stepNumber": m["stepNumber"],
                "stage": m["duration"],
                "duration": m["duration"],
                "skills": m["skillsToAcquire"][:3],
                "description": m["description"]
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
        "overview": f"Curated curriculum for transitioning into {role.strip().title()} over {timeframe}.",
        "milestones": milestones,
        "nodes": nodes,
        "edges": edges,
        "isAiGenerated": False,
        "modelUsed": "offline-curated-template",
        "generatedAt": datetime.utcnow().isoformat() + "Z",
        "fallbackNotice": "Generated using verified offline curriculum templates. Configure GEMINI_API_KEY in server environment for dynamic, real-time Gemini Generative AI roadmaps."
    }

def get_fallback_job_analysis(job_description: str, user_skills: str = "") -> Dict[str, Any]:
    """Analyzes a job description via rule-based heuristics when AI is offline."""
    jd_lower = job_description.lower()
    user_skills_list = [s.strip().lower() for s in user_skills.split(",") if s.strip()]

    # Skill lexicon for extraction
    skill_dictionary = {
        "Python": ["python", "django", "flask", "fastapi"],
        "JavaScript / TypeScript": ["javascript", "typescript", "js", "ts", "node", "nodejs"],
        "React / Modern Web": ["react", "next.js", "vue", "angular", "tailwind"],
        "Cloud Computing (AWS / Azure / GCP)": ["aws", "azure", "gcp", "cloud", "s3", "ec2", "iam"],
        "Docker & Containerization": ["docker", "container", "dockerfile", "containers"],
        "Kubernetes & Orchestration": ["kubernetes", "k8s", "helm"],
        "CI/CD & DevOps Automation": ["ci/cd", "github actions", "gitlab", "jenkins", "pipeline"],
        "SQL & Relational Databases": ["sql", "postgresql", "mysql", "postgres", "rdbms"],
        "NoSQL & Cache": ["mongodb", "redis", "dynamodb", "cassandra"],
        "Linux & System Administration": ["linux", "bash", "shell", "ubuntu", "unix"],
        "Cybersecurity & Compliance": ["security", "cis", "soc2", "vulnerability", "encryption", "siem"],
        "Machine Learning & AI": ["machine learning", "deep learning", "pytorch", "tensorflow", "llm", "rag", "scikit-learn"],
        "REST APIs & Microservices": ["rest", "api", "apis", "microservices", "graphql"],
        "Testing & QA": ["testing", "unit test", "pytest", "jest", "cypress", "e2e"]
    }

    soft_skill_keywords = {
        "Cross-functional Collaboration": ["cross-functional", "team", "collaborate", "stakeholders"],
        "Problem Solving & Analytical Thinking": ["problem-solving", "analytical", "troubleshoot", "debugging"],
        "Clear Technical Communication": ["communication", "presentation", "document", "documentation"],
        "Agile / Scrum Methodologies": ["agile", "scrum", "sprints", "jira"]
    }

    # Detect extracted technical skills
    detected_tech = []
    for skill_name, aliases in skill_dictionary.items():
        if any(alias in jd_lower for alias in aliases):
            detected_tech.append(skill_name)
    if not detected_tech:
        detected_tech = ["Core Domain Technical Skills", "Analytical Problem Solving", "Version Control (Git)"]

    # Detect soft skills
    detected_soft = []
    for s_name, aliases in soft_skill_keywords.items():
        if any(alias in jd_lower for alias in aliases):
            detected_soft.append(s_name)
    if not detected_soft:
        detected_soft = ["Strong Technical Communication", "Self-starter Mindset", "Team Collaboration"]

    # Extract responsibilities via sentence parsing
    responsibilities = []
    sentences = re.split(r'[\n\.\•\-\*]', job_description)
    for sent in sentences:
        clean = sent.strip()
        if len(clean) > 25 and any(w in clean.lower() for w in ["build", "develop", "manage", "design", "maintain", "collaborate", "lead", "implement", "ensure"]):
            responsibilities.append(clean)
            if len(responsibilities) >= 4:
                break
    if not responsibilities:
        responsibilities = [
            "Architect and maintain high-quality domain solutions following best practices.",
            "Collaborate with multi-disciplinary stakeholders to deliver key company milestones.",
            "Troubleshoot operational issues and improve overall system reliability.",
            "Write clean, testable, and maintainable documentation and code."
        ]

    # Calculate skill gaps
    matched_skills = []
    skill_gaps = []
    for tech in detected_tech:
        # Check if user mentioned this skill
        user_has = any(any(alias in u for alias in skill_dictionary.get(tech, [tech.lower()])) for u in user_skills_list)
        if user_has:
            matched_skills.append(tech)
        else:
            skill_gaps.append({
                "skill": tech,
                "importance": "High" if len(skill_gaps) < 2 else "Medium",
                "recommendation": f"Dedicate 10-15 hours to structured tutorials and build a targeted proof-of-concept project demonstrating {tech}."
            })

    total_req = len(detected_tech)
    match_score = int((len(matched_skills) / max(total_req, 1)) * 100) if user_skills_list else 45

    # Action plan
    action_plan = [
        f"Prioritize mastering {skill_gaps[0]['skill'] if skill_gaps else 'advanced domain patterns'} by creating a public GitHub repository.",
        "Align resume bullet points to mirror the exact responsibilities identified in this job description.",
        "Prepare concrete STAR-method interview anecdotes for team collaboration and technical troubleshooting.",
        "Take a focused skill assessment on CareerForge AI to benchmark your proficiency."
    ]

    return {
        "jobTitle": "Target Position (Extracted from Posting)",
        "companyType": "Technology / Enterprise",
        "experienceLevel": "Mid-Level" if "senior" not in jd_lower else "Senior",
        "requiredTechnicalSkills": detected_tech,
        "softSkills": detected_soft,
        "keyResponsibilities": responsibilities[:5],
        "userCurrentSkills": user_skills_list if user_skills_list else ["No user skills provided"],
        "matchedSkills": matched_skills,
        "skillGaps": skill_gaps,
        "matchScore": match_score,
        "actionPlan": action_plan,
        "isAiGenerated": False,
        "modelUsed": "offline-rule-based-analyzer",
        "fallbackNotice": "Parsed via offline heuristic rule-engine. Set GEMINI_API_KEY in server environment for deep AI contextual analysis of subtle job requirements."
    }

def get_fallback_assessment(role: str, difficulty: str = "Beginner", num_questions: int = 5) -> Dict[str, Any]:
    """Generates authentic multiple choice questions for role assessment."""
    role_norm = role.strip().lower()
    
    if "cloud" in role_norm or "security" in role_norm:
        all_q = [
            {
                "id": 1,
                "question": "Which AWS service is primarily used to monitor and manage user authentication and granular access permissions using least-privilege principles?",
                "options": ["AWS CloudWatch", "AWS IAM (Identity and Access Management)", "Amazon S3", "AWS Route 53"],
                "correctAnswerIndex": 1,
                "explanation": "AWS IAM allows you to specify who or what can access services and resources in AWS, centrally manage fine-grained permissions, and analyze access using IAM policies.",
                "testedSkill": "Cloud IAM & Access Control"
            },
            {
                "id": 2,
                "question": "What is the primary purpose of a Virtual Private Cloud (VPC) Security Group?",
                "options": [
                    "Acts as a stateful virtual firewall controlling inbound and outbound traffic at the instance level",
                    "Acts as a stateless firewall at the subnet level",
                    "Encrypts all data at rest on connected EBS volumes",
                    "Provides DNS domain registration services"
                ],
                "correctAnswerIndex": 0,
                "explanation": "Security Groups are stateful virtual firewalls that control inbound and outbound traffic for individual EC2 instances or network interfaces. Return traffic is automatically allowed regardless of outbound rules.",
                "testedSkill": "Network Security & Firewalls"
            },
            {
                "id": 3,
                "question": "In the context of DevSecOps, what does 'Shift-Left' security mean?",
                "options": [
                    "Delaying security audits until production deployment is complete",
                    "Integrating security controls, static code analysis, and testing early in the software development lifecycle",
                    "Moving all servers to the left availability zone for fault tolerance",
                    "Delegating all compliance responsibility exclusively to third-party auditors"
                ],
                "correctAnswerIndex": 1,
                "explanation": "Shift-Left refers to identifying and addressing security vulnerabilities as early as possible in the development pipeline (during coding and build steps) rather than waiting for post-deployment penetration testing.",
                "testedSkill": "DevSecOps Fundamentals"
            },
            {
                "id": 4,
                "question": "Which protocol is utilized to securely exchange cryptographic keys and establish an encrypted tunnel in HTTPS?",
                "options": ["FTP", "SNMP", "TLS (Transport Layer Security)", "DHCP"],
                "correctAnswerIndex": 2,
                "explanation": "TLS (and historically SSL) provides end-to-end communications security, authentication, and data integrity over computer networks such as the web.",
                "testedSkill": "Cryptography & PKI"
            },
            {
                "id": 5,
                "question": "What is a zero-trust network architecture primarily predicated upon?",
                "options": [
                    "Trusting any device that connects from within the corporate office intranet",
                    "Never trust, always verify: requiring authentication and authorization for every request regardless of origin",
                    "Disabling all user passwords and relying purely on IP whitelisting",
                    "Allowing open firewall access within internal subnets"
                ],
                "correctAnswerIndex": 1,
                "explanation": "Zero Trust operates on the principle of 'never trust, always verify'. No entity (inside or outside the perimeter) is trusted by default; continuous authentication and contextual authorization are strictly required.",
                "testedSkill": "Zero Trust Architecture"
            }
        ]
    elif "ai" in role_norm or "machine learning" in role_norm or "data" in role_norm:
        all_q = [
            {
                "id": 1,
                "question": "What is the primary risk of training a machine learning model with excessive capacity on a small dataset without regularization?",
                "options": ["High bias (Underfitting)", "High variance (Overfitting)", "Gradient Vanishing", "Loss of floating-point precision"],
                "correctAnswerIndex": 1,
                "explanation": "When model complexity exceeds the data's informational capacity, the model memorizes the noise in the training set, leading to high variance (overfitting) and poor generalization on unseen validation data.",
                "testedSkill": "Bias-Variance Tradeoff"
            },
            {
                "id": 2,
                "question": "Which evaluation metric is most appropriate for evaluating a fraud detection model where fraudulent transactions constitute only 0.1% of the total dataset?",
                "options": ["Raw Accuracy", "Precision-Recall AUC (or F1-Score on the positive class)", "Mean Squared Error", "R-squared"],
                "correctAnswerIndex": 1,
                "explanation": "With severe class imbalance, a trivial model predicting 'non-fraud' for everything achieves 99.9% accuracy. PR-AUC and F1-score specifically evaluate the trade-off between false positives and false negatives on the minority class.",
                "testedSkill": "Model Evaluation Metrics"
            },
            {
                "id": 3,
                "question": "What is the primary role of the Self-Attention mechanism in the Transformer architecture?",
                "options": [
                    "Downsampling feature maps using max pooling",
                    "Allowing each token in a sequence to dynamically weigh its relationship with all other tokens simultaneously",
                    "Compressing weights into integer 8-bit representations",
                    "Enforcing Markovian sequential constraints like an RNN"
                ],
                "correctAnswerIndex": 1,
                "explanation": "Self-Attention computes query-key dot products to assign attention weights across all tokens in parallel, capturing long-range contextual relationships far better than sequential recurrent models.",
                "testedSkill": "Deep Learning & Transformers"
            },
            {
                "id": 4,
                "question": "In Retrieval-Augmented Generation (RAG), what is the purpose of embedding documents into a vector database?",
                "options": [
                    "To compress document file sizes for cheaper cold storage",
                    "To enable semantic similarity search between the user query and relevant context chunks",
                    "To convert natural language into executable SQL queries directly",
                    "To replace the language model's pre-trained neural network entirely"
                ],
                "correctAnswerIndex": 1,
                "explanation": "Embedding chunks into high-dimensional vector space allows cosine-similarity or kNN search to retrieve the most semantically relevant context chunks corresponding to a user query at inference time.",
                "testedSkill": "RAG & Vector Search"
            },
            {
                "id": 5,
                "question": "Which technique is commonly used to prevent overfitting by randomly deactivating a subset of neurons during training?",
                "options": ["Dropout", "Batch Normalization", "Gradient Clipping", "Teacher Forcing"],
                "correctAnswerIndex": 0,
                "explanation": "Dropout randomly sets a fraction of activations to zero during each forward training pass, preventing co-adaptation of feature representations and improving model generalization.",
                "testedSkill": "Neural Network Regularization"
            }
        ]
    else:
        all_q = [
            {
                "id": 1,
                "question": "In software architecture, what is the main benefit of decoupling services through asynchronous message queues (e.g., RabbitMQ, SQS)?",
                "options": [
                    "Eliminating the need for databases",
                    "Buffer burst traffic, prevent cascading failures, and allow independent scaling of producer and consumer services",
                    "Guaranteed sub-millisecond synchronous UI responses",
                    "Automatic generation of frontend UI templates"
                ],
                "correctAnswerIndex": 1,
                "explanation": "Message queues introduce asynchronous decoupling: if consumer services experience temporary slowdowns or outages, the queue buffers incoming requests, preventing data loss and isolating failure domains.",
                "testedSkill": "Distributed Systems Design"
            },
            {
                "id": 2,
                "question": "What does an HTTP 429 status code signify when communicating with a modern web API?",
                "options": [
                    "Resource Not Found",
                    "Internal Server Error",
                    "Too Many Requests / Rate Limit Exceeded",
                    "Bad Gateway"
                ],
                "correctAnswerIndex": 2,
                "explanation": "HTTP 429 Too Many Requests indicates that the user or client has sent too many requests in a given amount of time (rate limit exceeded) and should back off before retrying.",
                "testedSkill": "API Integration & Protocols"
            },
            {
                "id": 3,
                "question": "Which database indexing strategy is most effective for speeding up queries filtering by multiple specific columns together?",
                "options": ["A Composite (Multi-column) B-Tree Index", "A Single-column Hash Index", "A Full-text Index", "No index (Full Table Scan)"],
                "correctAnswerIndex": 0,
                "explanation": "A composite index combines multiple columns into a single index structure, allowing the database query planner to rapidly satisfy multi-column WHERE conditions using the index tree directly.",
                "testedSkill": "Database Optimization"
            },
            {
                "id": 4,
                "question": "What is the primary function of a Content Delivery Network (CDN)?",
                "options": [
                    "To compile source code into machine executables",
                    "To cache static assets at edge locations geographically closer to users to reduce latency and origin server load",
                    "To securely manage database transaction rollbacks",
                    "To execute heavy background batch processing jobs"
                ],
                "correctAnswerIndex": 1,
                "explanation": "CDNs distribute copies of static content (images, JavaScript, CSS, videos) across a worldwide network of edge point-of-presence (PoP) servers, drastically reducing round-trip time (RTT).",
                "testedSkill": "Web Performance & Infrastructure"
            },
            {
                "id": 5,
                "question": "In modern CI/CD pipelines, why is automated linting and static analysis executed before running tests?",
                "options": [
                    "To detect syntax errors, code smells, and style violations instantly without the resource overhead of spinning up test environments",
                    "To automatically rewrite all business logic",
                    "Because tests cannot run if code comments are present",
                    "To delete unused database tables"
                ],
                "correctAnswerIndex": 0,
                "explanation": "Linters and static analyzers (like Oxlint, ESLint, Flake8) perform fast lexical and AST analysis in milliseconds, catching trivial bugs and security misconfigurations before costlier integration test stages run.",
                "testedSkill": "CI/CD & Code Quality"
            }
        ]

    selected = all_q[:num_questions]
    return {
        "role": role.strip().title(),
        "difficulty": difficulty,
        "questions": selected,
        "isAiGenerated": False,
        "modelUsed": "offline-curated-question-bank",
        "fallbackNotice": "Loaded from curated technical assessment bank. Add GEMINI_API_KEY in server environment for dynamically synthesized real-time questions customized to any arbitrary role or subtopic."
    }

def get_fallback_adapted_recommendations(
    role: str,
    score: int,
    total_questions: int,
    correct_skills: List[str],
    missed_skills: List[str]
) -> Dict[str, Any]:
    """Generates adapted remedial learning plan based on assessment outcomes."""
    percentage = int((score / max(total_questions, 1)) * 100)
    
    if percentage >= 80:
        overall_eval = f"Outstanding performance ({score}/{total_questions} - {percentage}%)! You have demonstrated solid foundational comprehension for {role.strip().title()}."
        remedial_priority = "Advanced Specialization"
    elif percentage >= 50:
        overall_eval = f"Promising baseline ({score}/{total_questions} - {percentage}%). You have core awareness but need targeted hands-on reinforcement in identified gap areas."
        remedial_priority = "Focused Remediation"
    else:
        overall_eval = f"Foundational review needed ({score}/{total_questions} - {percentage}%). Dedicating structured time to fundamental concepts will rapidly elevate your skill ceiling."
        remedial_priority = "Essential Foundations"

    strengths = correct_skills if correct_skills else ["Eagerness to benchmark skills and diagnose knowledge gaps"]
    weaknesses = missed_skills if missed_skills else ["Further practical edge-case testing under interview conditions"]

    personalized_plan = []
    for skill in weaknesses:
        personalized_plan.append({
            "priority": "Immediate" if len(personalized_plan) == 0 else "High",
            "topic": skill,
            "actionItem": f"Complete 2 practical lab exercises covering {skill}. Document key architectural takeaways in your notes.",
            "estimatedHours": "6-8 hours",
            "recommendedResources": [
                f"Official documentation and RFC deep-dives for {skill}",
                "Interactive hands-on sandbox labs (e.g. Katacoda, Cloud Academy, TryHackMe, LeetCode)",
                "Open-source implementation study in top GitHub repos"
            ]
        })

    if not personalized_plan:
        personalized_plan.append({
            "priority": "Medium",
            "topic": "Advanced System Design & Scalability",
            "actionItem": "Read through real-world tech post-mortems (e.g. Netflix TechBlog, AWS architecture center) to see how top teams handle failure modes.",
            "estimatedHours": "5 hours",
            "recommendedResources": ["System Design Primer GitHub Repo", "High Scalability Blog"]
        })

    hands_on_projects = [
        {
            "title": f"{role.strip().title()} Diagnostic Proof-of-Concept",
            "description": f"Build a focused mini-application specifically demonstrating mastery over: {', '.join(weaknesses[:2]) if weaknesses else 'core system workflows'}.",
            "targetedSkills": weaknesses[:3] if weaknesses else ["End-to-End Implementation"]
        },
        {
            "title": "Interactive Monitoring & Verification Dashboard",
            "description": "Instrument your application with metrics, logging, and error handling so you can diagnose runtime anomalies in real time.",
            "targetedSkills": ["Observability", "Testing", "Resilience"]
        }
    ]

    adjustment = f"Your current roadmap priority is to complete remedial drills for: {', '.join(weaknesses[:2]) if weaknesses else 'advanced capstone milestones'} before scheduling mock interviews."

    return {
        "role": role.strip().title(),
        "score": score,
        "totalQuestions": total_questions,
        "percentage": percentage,
        "overallEvaluation": overall_eval,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "personalizedPlan": personalized_plan,
        "handsOnProjects": hands_on_projects,
        "nextMilestoneAdjustment": adjustment,
        "isAiGenerated": False,
        "modelUsed": "offline-adaptive-rule-engine",
        "fallbackNotice": "Calculated via offline adaptive rule system. Add GEMINI_API_KEY in server environment for bespoke AI learning plan synthesis."
    }

def get_fallback_guidance(messages: List[Dict[str, str]], context: Dict[str, Any] = None) -> Dict[str, Any]:
    """Generates contextual career guidance when AI chat is offline."""
    last_query = messages[-1]["content"].lower() if messages else "how do i grow my career?"
    role = context.get("currentRole", "Software Engineering") if context else "Tech Professional"
    score = context.get("assessmentScore", None) if context else None
    
    reply = (
        f"### Career Navigation Advisory for {role}\n\n"
        f"Here are strategic recommendations based on current industry standards:\n\n"
        f"1. **Proof of Execution Over Certificates**: Employers increasingly value verifiable GitHub repositories with descriptive READMEs, architectural diagrams, and automated CI test passes over passive course certificates.\n\n"
        f"2. **Targeted Gap Bridging**: Focus on building 2 high-impact, production-grade portfolio projects rather than 10 generic tutorials. For each project, write a 1-page design document explaining the trade-offs you made.\n\n"
        f"3. **Interview Preparation Strategy**: Balance 60% system architecture & conceptual mastery with 40% practical problem-solving. Practice explaining your decision-making out loud.\n\n"
        f"*(Note: To unlock live open-ended conversational advice customized to your exact situation, configure `GEMINI_API_KEY` in the server `.env` file.)*"
    )
    
    if score is not None:
        reply += f"\n\n**Assessment Insight**: You recently benchmarked with a score of {score}%. Be sure to review the personalized remedial action items in your Assessment tab!"

    suggested = [
        f"What are the top 3 interview questions for {role}?",
        "How can I structure a portfolio project to impress senior hiring managers?",
        "What are the best strategies to transition into this role with non-traditional experience?"
    ]

    return {
        "reply": reply,
        "suggestedNextQuestions": suggested,
        "isAiGenerated": False,
        "modelUsed": "offline-guidance-template",
        "fallbackNotice": "Offline guidance template active. Configure GEMINI_API_KEY on the server to chat with real-time Gemini Generative AI."
    }
