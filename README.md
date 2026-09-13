# Prodigal AI — Multi-Agent Social Media AI

## AI Intern Hiring Task 1

**Candidate:** Sejal Srivastava  
**Task:** Multi-Agent Social Media AI System  
**Model:** Llama 3 8B via Ollama  
**Platform:** Python + Streamlit + FastAPI + SQLite

---

## 1. Overview

This project is a local, multi-agent AI system for planning, creating, publishing, and analyzing social media campaigns.

The system takes a human campaign brief and passes it through specialized agents:

1. Strategy Agent
2. Content Writer Agent
3. Creative Agent
4. Human Review Gate
5. Publisher Agent
6. Analytics Agent

The system then uses Week 1 performance to create an improved Week 2 campaign and compares the results.

The main objective is to demonstrate a **closed-loop AI workflow** rather than a single prompt generating social media content.

---

## 2. Architecture

The system uses a sequential multi-agent architecture with a shared campaign state.

```text
                         HUMAN CAMPAIGN BRIEF
                                  |
                                  v
                       +----------------------+
                       |    STRATEGY AGENT    |
                       | Audience + channels  |
                       | Campaign direction   |
                       +----------+-----------+
                                  |
                                  v
                       +----------------------+
                       | CONTENT WRITER AGENT |
                       | Captions + hashtags  |
                       | Platform copy        |
                       +----------+-----------+
                                  |
                                  v
                       +----------------------+
                       |    CREATIVE AGENT    |
                       | Visual direction     |
                       | Creative briefs      |
                       +----------+-----------+
                                  |
                                  v
                       +----------------------+
                       |   HUMAN REVIEW GATE  |
                       | Approve / revise     |
                       +----------+-----------+
                                  |
                                  v
                       +----------------------+
                       |   PUBLISHER AGENT    |
                       | Publish to mock API  |
                       +----------+-----------+
                                  |
                                  v
                       +----------------------+
                       |   MOCK SOCIAL MEDIA  |
                       |   PLATFORM + SQLite  |
                       +----------+-----------+
                                  |
                                  v
                       +----------------------+
                       |   ANALYTICS AGENT    |
                       | Performance analysis |
                       | Recommendations     |
                       +----------+-----------+
                                  |
                                  v
                       +----------------------+
                       |     WEEK 2 LOOP      |
                       | Apply learnings      |
                       | Re-publish + compare |
                       +----------------------+
```

### Local Model Layer

All AI generation is performed locally using **Ollama**.

No hosted LLM API is required for the main application flow.

The application uses:

- Python
- Ollama
- Llama 3 8B
- Streamlit
- FastAPI
- SQLite
- Pydantic

---

## 3. Agents

### Strategy Agent

The Strategy Agent converts the human campaign brief into a structured campaign strategy.

Responsibilities:

- Identify the target audience
- Determine campaign direction
- Select suitable channels
- Define content direction
- Maintain the original campaign objective

---

### Content Writer Agent

The Content Writer Agent converts the strategy into platform-ready social media posts.

Responsibilities:

- Write captions
- Generate hashtags
- Adapt copy to the selected channel
- Maintain the target audience and campaign objective

The system also normalizes hashtags before publishing to prevent malformed hashtag data.

---

### Creative Agent

The Creative Agent converts the campaign strategy and content into creative direction.

Responsibilities:

- Generate creative briefs
- Define visual direction
- Connect creative concepts to campaign objectives
- Provide information that can be reviewed before publishing

---

### Publisher Agent

The Publisher Agent handles the final publishing stage.

Responsibilities:

- Send approved posts to the mock social media API
- Preserve post metadata
- Record the channel
- Record content
- Record hashtags
- Record posting time
- Collect simulated performance metrics

---

### Analytics Agent

The Analytics Agent analyzes published campaign results.

Responsibilities:

- Summarize campaign performance
- Compare channels when enough evidence exists
- Analyze available content characteristics
- Identify useful patterns
- Generate actionable recommendations
- Avoid unsupported causal claims

The analytics layer is intentionally conservative.

For example, if all posts use the same number of hashtags, the system does not claim that hashtag count caused performance differences.

---

## 4. Human Review Gate

The system includes a human approval step between content generation and publishing.

The workflow is:

```text
AI generates campaign
        |
        v
Human reviews campaign
        |
        +---- Revise
        |
        v
Approve
        |
        v
Publisher Agent
```

This prevents AI-generated content from automatically being published without review.

---

## 5. Mock Social Media Platform

A custom mock social media platform is included in the project.

It is implemented using:

- FastAPI
- SQLite
- Pydantic

The API accepts social media posts and generates simulated performance metrics.

Example publishing flow:

```text
Publisher Agent
      |
      v
FastAPI Mock Platform
      |
      v
SQLite Database
      |
      v
Simulated Metrics
```

The platform provides a controlled environment for testing the complete campaign lifecycle.

---

## 6. Hidden Simulator Rules

The mock platform contains hidden performance rules so that the analytics system has to discover useful signals from observed data.

The current simulator includes four important rules.

| Variable | Hidden Rule |
|---|---|
| Reel caption length | Shorter Reel copy receives a views boost; very long copy receives a penalty |
| Carousel content | Carousel posts containing a save-oriented message receive higher saves and additional views |
| Hashtag count | 3–5 hashtags receive a small boost; more than 8 hashtags receive a penalty |
| Posting time | Posts published between 10:00 and 12:00 receive a performance boost |

These rules are implemented inside the simulator rather than directly exposed to the analytics agent.

### Rules intentionally not implemented

The task suggested additional signals such as question-ending boosts and novelty decay.

These were not implemented in the current version.

This keeps the simulator intentionally scoped while still providing multiple variables for the analytics loop to investigate.

---

## 7. Campaign Formation

The campaign starts with a human-written brief.

The Strategy Agent converts the brief into structured campaign information.

The following agents then progressively enrich the shared state:

```text
Human Brief
    ↓
Strategy
    ↓
Content
    ↓
Creative
    ↓
Human Review
    ↓
Publishing
```

Each stage has a specific responsibility rather than asking one model prompt to perform the entire workflow.

---

## 8. Shared Campaign State

The agents communicate through a shared campaign state.

The state contains information such as:

- Human campaign brief
- Target audience
- Channel mix
- Drafted posts
- Creative briefs
- Feedback

This allows downstream agents to use the output of previous agents.

The design also makes the workflow easier to debug because each stage has a defined input and output.

---

## 9. Structured Output and Reliability

The local model is prompted to return structured JSON.

The application validates and normalizes the generated information before passing it to the next stage.

Examples of reliability checks include:

- JSON parsing
- Hashtag normalization
- Missing-field handling
- Channel preservation
- Post metadata preservation
- Defensive defaults

The system also includes fallback handling for malformed model output.

---

## 10. Analytics Guardrails

The analytics layer is designed to avoid overclaiming.

### Single-post campaigns

When only one post is available, the system does not attempt to make comparative claims.

Instead, it reports:

- Observed metrics
- Available content characteristics
- Lack of sufficient comparative evidence

### Multiple posts

Comparisons are only made when there is enough variation in the relevant variable.

For example:

```text
If every post has 3 hashtags:

Do not conclude:
"3 hashtags perform best."

Instead conclude:
"There is insufficient variation in hashtag count to evaluate its effect."
```

This prevents the analytics system from treating constant variables as evidence.

---

## 11. Week 1 Analysis

After Week 1 publishing, the system collects simulated performance metrics.

The Analytics Agent analyzes the results and produces:

- Performance summary
- Channel-level observations
- Evidence-backed insights
- Recommendations for the next campaign

The recommendations are then used as input to the Week 2 campaign.

---

## 12. Week 2 Closed Loop

Week 2 is not simply another independent campaign.

The Week 2 brief is generated from:

```text
Original Campaign Brief
          +
Week 1 Performance
          +
Week 1 Recommendations
          |
          v
     Week 2 Brief
```

The original campaign objective and target audience are preserved.

The purpose is to test whether applying Week 1 learnings changes subsequent performance.

---

## 13. Example Week 1 → Week 2 Comparison

One demonstration run produced the following results.

### Week 1

| Metric | Result |
|---|---:|
| Posts | 2 |
| Views | 9,131 |
| Likes | 514 |
| Comments | 30 |
| Saves | 70 |

### Week 2

| Metric | Result |
|---|---:|
| Posts | 2 |
| Views | 5,046 |
| Likes | 288 |
| Comments | 24 |
| Saves | 71 |

### Comparison

| Metric | Week 1 | Week 2 | Change |
|---|---:|---:|---:|
| Views | 9,131 | 5,046 | -4,085 |
| Likes | 514 | 288 | -226 |
| Comments | 30 | 24 | -6 |
| Saves | 70 | 71 | +1 |

The results demonstrate the complete feedback loop.

Importantly, the system does not assume that every Week 2 recommendation will automatically improve every metric.

The simulator is stochastic, so performance can vary between runs.

---

## 14. Example Analytics Recommendations

A typical Week 1 analysis can produce recommendations such as:

1. Prioritize the better-performing channel while retaining another channel for comparison.
2. Repeat strong-performing patterns across multiple posts to test whether the result is reproducible.
3. Keep the target audience and campaign objective constant while testing one execution variable at a time.

The recommendations are intentionally conservative because the system should distinguish between an observation and a proven causal relationship.

---

## 15. Streamlit Interface

The project includes a Streamlit frontend.

The interface supports:

- Campaign brief input
- Campaign generation
- Strategy review
- Generated content review
- Creative brief review
- Human approval
- Publishing
- Week 1 analytics
- Week 2 campaign generation
- Week 2 performance comparison

The application is designed as an interactive campaign workflow rather than a static analytics dashboard.

---

## 16. Running the Project

### Step 1 — Clone the repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd Prodigal_AI_Task1_Sejal_shrivastava_23BAI10851
```

### Step 2 — Create a virtual environment

```bash
python3 -m venv venv
```

### Step 3 — Activate the environment

```bash
source venv/bin/activate
```

### Step 4 — Install dependencies

```bash
pip install -r requirements.txt
```

### Step 5 — Install and start Ollama

Install Ollama separately and make sure the required local model is available.

Example:

```bash
ollama run llama3
```

The application uses the local Ollama runtime rather than a hosted LLM API.

### Step 6 — Start the mock platform

Open a terminal and run:

```bash
uvicorn mock_platform:app --host 0.0.0.0 --port 8000
```

Keep this terminal running.

### Step 7 — Start Streamlit

Open another terminal:

```bash
streamlit run app.py
```

The Streamlit interface will then be available locally.

---

## 17. Project Structure

```text
Prodigal_AI_Task1_Sejal_shrivastava_23BAI10851/
│
├── agents.py
├── app.py
├── mock_platform.py
├── ollama_wrapper.py
├── APIwrapper.py
├── requirements.txt
├── README.md
├── mock_instagram.db
├── Prodigal_AI_Task1_Sejal_Srivastava_Submission_Writeup.pdf
│
├── agents_backup.py
│
└── .gitignore
```

### Important files

**`agents.py`**  
Contains the multi-agent orchestration and agent responsibilities.

**`app.py`**  
Streamlit frontend.

**`mock_platform.py`**  
FastAPI mock social media platform and simulator.

**`ollama_wrapper.py`**  
Local Ollama model interface.

**`APIwrapper.py`**  
Local model wrapper / structured generation utility.

**`mock_instagram.db`**  
SQLite storage for the mock platform.

---

## 18. Engineering Decisions

### Local model

A local Llama 3 model was selected through Ollama to satisfy the requirement of avoiding hosted LLM APIs.

### Multi-agent design

The system separates strategy, content, creative generation, publishing, and analytics instead of using one large prompt.

### Mock platform

A custom FastAPI + SQLite platform provides an actual publishing and measurement environment.

### Conservative analytics

The analytics system checks whether sufficient variation exists before making comparisons.

### Closed-loop execution

Week 2 is generated using Week 1 findings so the system demonstrates iterative learning.

---

## 19. Failure Modes Considered

The system accounts for several practical failure cases.

### Malformed model output

Structured parsing and defensive defaults prevent the entire pipeline from failing when generated JSON is imperfect.

### Missing metadata

Publishing logic preserves channel, content, hashtags, and posting time so analytics can inspect the relevant variables.

### Insufficient evidence

The analytics system avoids comparisons when there are too few observations.

### Constant variables

A variable with only one observed value is not treated as evidence of performance impact.

### Stochastic simulator

Because the simulator contains randomness, different executions can produce different performance numbers.

Therefore, the system focuses on repeatable patterns and controlled testing rather than assuming one run proves causality.

---

## 20. Limitations and Future Improvements

The current implementation intentionally keeps the scope manageable.

Potential future improvements include:

- Add a Community Manager Agent
- Add a Brand & Compliance Agent
- Add question-ending engagement rules
- Add novelty decay across repeated content
- Add richer channel-specific simulators
- Run larger A/B experiments
- Store historical campaign learning across many weeks
- Add stronger statistical significance testing
- Add real image generation through a local model
- Add authentication and multi-user support

These improvements would make the system more suitable for production use.

---

## 21. Requirement Coverage

| Requirement | Implementation |
|---|---|
| Local/open-weight model | Llama 3 through Ollama |
| No hosted LLM API in main flow | Yes |
| Multi-agent architecture | Strategy, Content, Creative, Publisher, Analytics |
| Human review | Approval gate before publishing |
| Mock social platform | FastAPI + SQLite |
| Campaign creation | Human brief → strategy → content → creative |
| Weekly analysis | Analytics Agent |
| Hidden simulator rules | Implemented |
| Week 2 loop | Implemented |
| Before/after comparison | Implemented |
| Reproducible setup | README + requirements |
| Write-up | Submission PDF included |

---

## 22. Conclusion

This project demonstrates a complete AI-assisted social media campaign lifecycle:

```text
Human Brief
     ↓
Strategy
     ↓
Content
     ↓
Creative
     ↓
Human Review
     ↓
Publish
     ↓
Measure
     ↓
Analyze
     ↓
Improve
     ↓
Week 2
```

The key focus of the project is not simply generating social media content.

It is demonstrating how multiple specialized agents can work together with a mock platform and an analytics feedback loop to support iterative campaign improvement.

---

## Submission

This repository contains:

- Source code
- Multi-agent implementation
- Mock social media platform
- SQLite demo database
- Requirements file
- README documentation
- Submission write-up PDF

No model weights or virtual environment files are included in the repository.
