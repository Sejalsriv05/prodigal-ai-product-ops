

````markdown
# Prodigal AI — Multi-Agent Social Media AI

## AI Intern Hiring Task 1

**Candidate:** Sejal Srivastava  
**College:** VIT Bhopal University  
**Project:** Build a Multi-Agent Social Media AI Company

---

## 1. Overview

This project implements a fully local, multi-agent social media campaign system.

The system takes a human-written campaign brief and converts it into:

- Campaign strategy
- Target audience and channel mix
- Social media post copy
- Hashtags and CTAs
- Per-post creative briefs
- Human-reviewed campaign
- Published posts on a self-built mock social media platform
- Simulated audience engagement
- Weekly analytics
- Recommendations for the next week
- A Week 2 campaign based on Week 1 learnings

The complete LLM pipeline runs locally using **Ollama** and does not depend on hosted LLM APIs.

---

# 2. Architecture

The project uses a custom sequential multi-agent orchestration approach with a shared campaign state.

```text
                    ┌─────────────────────┐
                    │    HUMAN BRIEF      │
                    │   Streamlit UI      │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   STRATEGY AGENT    │
                    │ Audience / Strategy │
                    │ Channel Mix / KPIs  │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ CONTENT WRITER      │
                    │ Copy / Hooks / CTA  │
                    │ Hashtags / Tone     │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   CREATIVE AGENT    │
                    │ Visual / Asset Brief│
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │  HUMAN REVIEW GATE  │
                    │  Approve / Reject   │
                    └──────────┬──────────┘
                               │
                         APPROVED
                               │
                               ▼
                    ┌─────────────────────┐
                    │   PUBLISHER AGENT   │
                    │   API Integration   │
                    └──────────┬──────────┘
                               │
                               ▼
              ┌─────────────────────────────────┐
              │     MOCK SOCIAL PLATFORM        │
              │        FastAPI + SQLite         │
              │                                 │
              │ Posts → Simulation → Metrics    │
              └────────────────┬────────────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   ANALYTICS AGENT   │
                    │ Performance / Why   │
                    │ Recommendations     │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │      WEEK 2         │
                    │ Apply Week 1        │
                    │ Recommendations     │
                    └──────────┬──────────┘
                               │
                               └──────────────►
                                  Review → Publish
                                  → Analyse → Compare
````

---

# 3. Agents

## Strategy Agent

Converts the human brief into campaign strategy.

It determines the target audience, campaign direction, channel mix, objectives and content approach.

## Content Writer Agent

Creates the actual social media copy.

It generates hooks, calls-to-action, hashtags and channel-aware content while following the campaign requirements.

## Creative Agent

Creates a creative/visual brief for every post.

It describes the visual asset, lighting, rendering style, camera angle, composition and overall creative direction.

## Publisher Agent

Publishes approved posts to the mock social media platform.

It converts the generated campaign data into API requests and stores the published posts through the platform.

## Analytics Agent

Reads campaign performance from the mock platform.

It identifies supported patterns, explains possible reasons and generates concrete recommendations for the next week.

## Human Review Gate

The human operator remains in control of publishing.

Generated posts must be reviewed and explicitly approved through the UI before the Publisher Agent can publish them.

---

# 4. Local Model Layer

The project uses:

**Model:** Llama 3 8B
**Runtime:** Ollama
**Ollama Version:** 0.34.0
**Python:** 3.13.5
**Development Hardware:** MacBook Air

The LLM is accessed through a thin local wrapper.

No hosted LLM APIs are required by the main pipeline.

The system does not use:

* OpenAI API
* Anthropic API
* Gemini API
* Groq API
* Other hosted LLM APIs

This satisfies the fully-local execution requirement.

---

# 5. Reliability and Structured Output

Local models can occasionally produce malformed JSON or additional conversational text.

The local model wrapper therefore uses:

* Structured JSON output requirements
* JSON parsing and validation
* Retry handling for malformed responses
* A bounded retry process instead of allowing invalid output to propagate through the pipeline

This makes the agent pipeline more reliable when running with a local model.

---

# 6. Mock Social Media Platform

The mock platform is built specifically for this project.

### Technology

* FastAPI
* SQLite
* Python

The Publisher Agent communicates with the platform through an API.

The platform provides persistent storage for published posts and simulated engagement data.

Post information includes:

* Channel
* Content
* Hashtags
* Posting time
* Creative brief
* Engagement metrics

---

# 7. Simulated Engagement Model

The simulator does not use completely random engagement.

It starts with a random baseline and then applies deterministic rules based on post characteristics.

This makes the platform suitable for testing whether the Analytics Agent can discover meaningful patterns.

## Hidden Rules

### 1. Reel Caption Length

Reels with captions of 40 words or fewer receive a view boost.

Reels with captions above 80 words receive a view penalty.

### 2. Carousel + Save Language

Carousel posts containing language related to saving receive increased saves and an additional view boost.

### 3. Hashtag Count

Hashtag count has a non-linear effect.

* More than 8 hashtags reduces views and likes.
* 3–5 hashtags provides a moderate view boost.

### 4. Posting Time

Posts published between 10:00 and 12:00 receive increased views and likes.

### Signals Not Implemented

Two example signals from the task were intentionally not implemented in the current simulator:

* Question-ending engagement boost
* Novelty decay when the same format repeats

These are documented separately rather than being presented as discovered features.

---

# 8. Campaign Creation Flow

The campaign starts from a human-written brief.

For example:

> We are launching a budget-friendly table fan for students. Run a short awareness campaign.

The system processes the brief through the agent pipeline:

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
Publisher
    ↓
Mock Platform
    ↓
Analytics
```

The Streamlit UI allows the human operator to change the campaign brief before running the workflow.

---

# 9. Human Approval

Publishing is intentionally separated from content generation.

The UI displays the generated campaign before publication.

The human can:

* Review the generated posts
* Approve the campaign
* Reject the campaign

Publishing only occurs after approval.

This prevents the system from automatically publishing unreviewed AI-generated content.

---

# 10. Weekly Analysis Loop

At the end of Week 1, the Analytics Agent analyses the simulated campaign results.

The report considers:

* Total performance
* Channel performance
* Content characteristics
* Hashtag variation
* Posting time
* Content length
* Performance differences between posts

The recommendation layer also applies evidence guardrails.

A variable is not recommended for modification when there is no meaningful variation in the observed data.

The system also avoids claiming causation from small samples.

---

# 11. Week 1 → Week 2 Improvement Loop

The strongest part of the system is the closed feedback loop.

```text
Week 1
  ↓
Publish
  ↓
Collect Metrics
  ↓
Analytics Agent
  ↓
Recommendations
  ↓
Create Week 2 Brief
  ↓
Strategy
  ↓
Content
  ↓
Creative
  ↓
Human Review
  ↓
Publish Week 2
  ↓
Compare Performance
```

The Week 2 campaign keeps the original campaign objective and target audience while incorporating the recommendations generated from Week 1.

This makes it possible to compare the two weeks rather than treating analytics as a standalone report.

---

# 12. Example Before / After Results

One demonstrated run produced the following results:

| Metric   | Week 1 | Week 2 | Change |
| -------- | -----: | -----: | -----: |
| Views    |  9,131 |  5,046 | -4,085 |
| Likes    |    514 |    288 |   -226 |
| Comments |     30 |     24 |     -6 |
| Saves    |     70 |     71 |     +1 |

Week 2 did not improve every metric.

Views, likes and comments decreased, while saves increased slightly.

This result is intentionally reported as observed rather than being presented as a fabricated improvement. The feedback loop therefore demonstrates measurement and iteration even when the second week does not outperform the first on every KPI.

---

# 13. Analytics Guardrails

The Analytics Agent uses conservative recommendations because the simulated campaigns may contain only a small number of posts.

Examples of guardrails include:

* Do not make comparisons when only one post exists.
* Do not recommend changing a variable when all observed posts use the same value.
* Do not claim causation from limited observations.
* Do not infer that longer or shorter content is universally better from a small sample.
* Prefer repeated patterns and channel-level differences.
* When evidence is insufficient, recommend controlled testing instead.

This prevents the weekly report from becoming a collection of unsupported assumptions.

---

# 14. Project Structure

```text
Prodigal_AI_Task1_Sejal_shrivastava_23BAI10851/
│
├── agents.py
├── APIwrapper.py
├── ollama_wrapper.py
├── mock_platform.py
├── app.py
├── mock_instagram.db
├── requirements.txt
├── README.md
└── ...
```

### Important files

**agents.py**

Contains the specialised agents and campaign orchestration.

**ollama_wrapper.py**

Provides the local Ollama model abstraction and structured response handling.

**mock_platform.py**

Contains the FastAPI mock social media platform and SQLite persistence.

**app.py**

Contains the Streamlit user interface and human review workflow.

**mock_instagram.db**

SQLite database used by the mock social media platform.

**requirements.txt**

Contains the Python dependencies required to run the project.

---

# 15. Installation

Clone or extract the project.

Create a virtual environment:

```bash
python3 -m venv venv
```

Activate it:

```bash
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Make sure Ollama is installed and available.

Pull/run the local model:

```bash
ollama run llama3
```

---

# 16. Running the Project

The system uses three processes.

## Terminal 1 — Ollama

```bash
ollama run llama3
```

Keep the model available while running the application.

## Terminal 2 — Mock Platform

Activate the virtual environment if necessary:

```bash
source venv/bin/activate
```

Start the API:

```bash
uvicorn mock_platform:app --host 0.0.0.0 --port 8000
```

The mock platform will run locally on port 8000.

## Terminal 3 — Streamlit UI

Activate the virtual environment:

```bash
source venv/bin/activate
```

Start the application:

```bash
streamlit run app.py
```

Streamlit will provide the local web interface.

---

# 17. Demo Flow

To reproduce the complete workflow:

1. Start Ollama with the local Llama 3 model.
2. Start the FastAPI mock social media platform.
3. Start the Streamlit application.
4. Enter a campaign brief.
5. Generate the campaign.
6. Review the generated posts.
7. Approve the campaign.
8. Publisher Agent sends the approved posts to the mock platform.
9. Analytics Agent generates the Week 1 report.
10. Use the recommendations to generate Week 2.
11. Review and publish Week 2.
12. Compare Week 1 and Week 2 metrics.

---

# 18. Engineering Decisions

A custom orchestration approach was used instead of a large agent framework.

The main reason was simplicity and transparency.

Each agent is implemented as a separate function with a clearly defined responsibility, and the shared CampaignState makes the handoff between agents explicit.

The project intentionally prioritises a smaller number of connected agents over adding agents that are not fully integrated into the workflow.

The current implementation focuses on:

* Strategy
* Content
* Creative
* Publishing
* Analytics
* Human approval

Community management and brand/compliance review were kept outside the core implementation rather than adding shallow agents that were not fully wired into the end-to-end loop.

---

# 19. Limitations

The current implementation has several limitations.

### Limited sample size

The demo uses a small number of posts per week, so some simulator signals cannot be reliably inferred from a single run.

### Missing simulator signals

Question-ending engagement and novelty decay are not currently implemented.

### Limited engagement metrics

The current simulator focuses on the core metrics used in the demonstrated run, including views, likes, comments and saves.

### Agent coverage

Community Manager and Brand & Compliance agents are not part of the current core pipeline.

---

# 20. Future Improvements

With additional development time, the system could be extended with:

* Community Manager Agent
* Brand & Compliance Agent
* Bounded rejection/revision loops
* Simulated comments and DM handling
* Sentiment analysis
* Shares
* Click-through rate
* Follower delta
* Question-ending engagement rule
* Novelty decay
* Larger campaign sample sizes
* Stronger statistical analysis
* Persistent campaign memory across multiple campaigns

---

# 21. Requirement Coverage

| Prodigal AI Requirement   | Implementation                                    |
| ------------------------- | ------------------------------------------------- |
| Ollama + local model      | Llama 3 8B through Ollama                         |
| No hosted LLM APIs        | Main pipeline uses local Ollama                   |
| Multi-agent architecture  | Five specialised agents                           |
| Separate responsibilities | Strategy, Content, Creative, Publisher, Analytics |
| Mock social platform      | Custom FastAPI + SQLite                           |
| Persistent storage        | SQLite                                            |
| Human campaign brief      | Streamlit input                                   |
| Human approval            | Approve / Reject gate                             |
| Campaign generation       | Strategy → Content → Creative                     |
| Publishing                | Publisher Agent → Mock Platform API               |
| Weekly analysis           | Analytics Agent                                   |
| Concrete recommendations  | Evidence-based recommendation layer               |
| Week 2 improvement loop   | Week 1 recommendations → Week 2                   |
| Hidden simulator rules    | Timing, length, hashtag and carousel/save effects |
| Demo data                 | SQLite database included                          |
| Dependency file           | requirements.txt                                  |
| Documentation             | README + PDF write-up                             |

---

# 22. Conclusion

This project demonstrates a local multi-agent workflow rather than a single LLM prompt.

The key design is the complete lifecycle:

```text
Human Brief
     ↓
Specialised Agents
     ↓
Human Review
     ↓
Mock Platform
     ↓
Simulated Audience
     ↓
Analytics
     ↓
Recommendations
     ↓
Week 2
```

The system is designed to make agent responsibilities, handoffs, human control and analytical reasoning visible.

The implementation also deliberately documents limitations and unsuccessful outcomes instead of presenting every experiment as a success.

