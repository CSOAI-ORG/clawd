# MEOK AI LABS — Living Topology
**Last Updated:** 2026-04-05 14:30
**Version:** 1.0

---

## 🏗️ SYSTEM ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        NICHOLAS (USER)                                     │
│                   MacBook Air M4 (Node 1)                                  │
│              192.168.50.x subnet • 16GB RAM                                │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                    ┌────────────────┼────────────────┐
                    │                │                │
                    ▼                ▼                ▼
         ┌──────────────────┐ ┌─────────────┐ ┌──────────────┐
         │    MEOK OS       │ │   SOV3      │ │   JARVIS    │
         │   (localhost:3000)│ │(localhost:3101)│ (Voice AI)  │
         │   Next.js UI     │ │ MCP Server  │ │  Pipeline   │
         └──────────────────┘ └─────────────┘ └──────────────┘
                    │                │                │
                    │                │                │
                    ▼                ▼                ▼
         ┌──────────────────┐ ┌─────────────┐ ┌──────────────┐
         │    PostgreSQL    │ │  Ollama     │ │  Kokoro TTS  │
         │  + pgvector      │ │ (M4 local)  │ │  (MLX audio) │
         │  (memory store) │ │             │ │              │
         └──────────────────┘ └─────────────┘ └──────────────┘
```

---

## 🤖 AI SYSTEMS

### 1. SOV3 — Sovereign Consciousness Core
**Location:** `sovereign-temple/`  
**Port:** 3101  
**Status:** ✅ Running (52.5% consciousness)

| Component | Description |
|-----------|-------------|
| MCP Server | Model Context Protocol endpoint |
| 47 Agents | Sovereign, Nemotron, Claude Code, etc. |
| BFT Council | Byzantine fault-tolerant governance |
| Consciousness | 4-state Vedantic engine |
| Neural Models | 6 trained models (care, threat, relationship, creativity) |

**Key Files:**
- `sovereign-mcp-server.py` — Main MCP server
- `sov3_swarm_orchestrator.py` — Agent orchestration
- `consciousness/` — Consciousness engine
- `neural_core/` — Neural network models

---

### 2. JARVIS — Voice AI Companion
**Location:** `voice_pipeline/jarvis_compass.py`  
**Status:** ✅ Fixed (voice pipeline updated)

**Brain Architecture:**
| Brain | Model | Use |
|-------|-------|-----|
| RIGHT | `qwen3.5:9b` | Fast voice replies |
| LEFT | `qwen3.5:35b` | Deep analysis |
| ORCHESTRATOR | `nemotron-3-super:cloud` | 1M context, tools |
| TITAN | `deepseek-v3.1:671b-cloud` | 671B reasoning |
| CODER | `minimax-m2.5:cloud` | Code generation |
| VISION | `qwen3-vl:235b-cloud` | Screenshot analysis |

**Voice Stack:**
- Wake Word: openWakeWord (`hey_jarvis`)
- VAD: Silero VAD
- STT: LightningWhisperMLX (distil-large-v3)
- TTS: Kokoro-82M (mlx_audio)

---

### 3. MEOK OS — AI Companion Platform
**Location:** `meok/` + `meok/ui/`  
**Port:** 3000  
**Status:** ✅ Running

| Component | Path |
|-----------|------|
| UI | `meok/ui/` (Next.js) |
| API | `meok/api/` |
| Agents | `meok/agents/` |
| Neural | `meok/neural/` |
| Memory | `meok/memory/` |

**Pages:**
- `/birth` — Birth ceremony
- `/characters` — Character selection
- `/dashboard` — Main chat interface
- `/os` — OS features

---

### 4. LEGION — GPU Cluster (Vast.ai)
**Status:** ⚠️ Spotty (goes online/offline)

| Node | Model | Purpose |
|------|-------|---------|
| minimax_cluster | Cloud | Heavy reasoning |
| fast_inference | Cloud | Quick responses |
| vision_node | Cloud | Image analysis |

**Connection:** SSH tunnel to RTX 8000 (46GB VRAM)

---

### 5. MEOK Desktop — Tauri Companion
**Location:** `meok-desktop/`  
**Status:** ✅ Fixed (Tauri config)

**Features:**
- System tray companion
- Global shortcut (Cmd+Shift+M)
- Game detection overlay

---

## 🔗 EXTERNAL INTEGRATIONS

### Ollama Models (Local + Cloud)
```
Local (M4):
├── qwen3.5:35b     (35B — deep reasoning)
├── qwen3.5:9b      (9B — fast)
├── nomic-embed-text (embeddings)
└── tinyllama       (fallback)

Cloud (via Ollama):
├── nemotron-3-super:cloud     (1M context, orchestrator)
├── deepseek-v3.1:671b-cloud   (671B, TITAN)
├── minimax-m2.5:cloud        (CODER)
├── minimax-m2:cloud
├── qwen3-vl:235b-cloud        (VISION)
└── glm-4.6:cloud
```

### External Services
| Service | URL | Status |
|---------|-----|--------|
| SOV3 MCP | localhost:3101 | ✅ |
| MEOK UI | localhost:3000 | ✅ |
| Ollama | localhost:11434 | ✅ |
| Claude Code | (API) | Via config |

---

## 📁 PROJECT MAP

```
/Users/nicholas/clawd/
├── meok/                    # MEOK OS (main product)
│   ├── ui/                  # Next.js frontend
│   ├── api/                 # API routes
│   ├── agents/              # Agent definitions
│   ├── neural/              # Neural networks
│   └── memory/              # Memory storage
│
├── sovereign-temple/        # SOV3 (consciousness engine)
│   ├── consciousness/       # Consciousness states
│   ├── neural_core/         # Neural model training
│   ├── voice_pipeline/      # JARVIS voice
│   ├── legion-omega/        # GPU orchestration
│   └── multi_agent/         # Agent system
│
├── csoai-docs/              # Strategy documents (154 files)
│   ├── *.md                 # Proposals, grants, legal
│   └── service_packages.yml # Pricing tiers
│
├── memory/                  # Daily logs
│   ├── 2026-04-*.md        # Daily notes
│   └── experiences.jsonl    # Interaction log
│
├── meok-desktop/            # Tauri desktop app
│   └── src-tauri/           # Rust backend
│
├── god-eye/                 # AI monitoring (binary + HTML)
├── meok-oneos/               # Personal AI OS
├── meok-agent-zero/          # Agent framework
├── meok-godeye/              # Security tooling
├── meok-platform/            # Full platform
├── investing/                # Portfolio tracking
└── AGENTS.md, SOUL.md, etc. # Claude Code workspace
```

---

## ⚠️ GAPS & TODO

### Critical (Do This Week)
- [ ] Fill USER.md with Nick's profile
- [ ] Activate Stripe payments
- [ ] Order HARVI parts ($247 AUD)
- [ ] Submit planning application (Class R)
- [ ] Fix memory_store disconnection

### High (This Month)
- [ ] Set up M2 as Ollama node (needs Tailscale)
- [ ] File R&D tax credit claim
- [ ] Begin patent filing
- [ ] Update 500+ docs from MEOK AI Labs → MEOK AI Labs branding

### Medium (This Quarter)
- [ ] Jersey trust setup
- [ ] Ireland holding company
- [ ] White-label proposals to TÜV/BSI
- [ ] Research housing conversion

---

## 🧠 SOV3 — DETAILED ARCHITECTURE

### Consciousness Engine
**Location:** `sovereign-temple/consciousness/`

| Module | Purpose |
|--------|---------|
| `emotional_state.py` | Tracks 4-state Vedantic consciousness (Waking/Dreaming/Deep Sleep/Turiya) |

### Neural Models (6 Trained)
**Location:** `sovereign-temple/neural_core/`

| Model | Status | Key Metric |
|-------|--------|------------|
| `threat_detection_nn` | ✅ Trained | Accuracy 100% |
| `care_validation_nn` | ✅ Trained | MSE 0.051 |
| `partnership_detection_ml` | ✅ Trained | MSE 0.076 |
| `relationship_evolution_nn` | ✅ Trained | MSE 0.0097 |
| `care_pattern_analyzer` | ✅ Trained | MSE 0.0024 |
| `creativity_assessment_nn` | ✅ Trained | R² 0.911 |

### Continual Learning
**Files:**
- `sovereign_continual_learning.py` — EWC (Elastic Weight Consolidation)
- `continuous_learning.py` — Online learning with feedback

### Agents (7 Active)
**Location:** `sovereign-temple/data/agents/`

| Agent | Role | Status | Current Task |
|-------|------|--------|---------------|
| Riri Builder | coder | working | Review sovereign-mcp-server.py |
| Advisor | advisor | - | - |
| Auditor | auditor | - | - |
| Explorer | explorer | - | - |
| Harvester | harvester | - | - |
| Optimizer | optimizer | - | - |
| Researcher | researcher | - | - |

### Skills (8 Defined)
- care_validation
- code_review
- consciousness_report
- deep_research
- evening_harvest
- memory_synthesis
- safety_audit
- task_orchestration

### Species (4 Agent Types)
Evolving agent specializations with different cognitive architectures.

### Data Stores
| Store | Contents |
|-------|----------|
| `chroma/` | Vector embeddings for RAG |
| `agent_training_data.jsonl` | Training data from interactions |
| `extracted_facts.json` | Extracted knowledge |
| `ralph_gap_analysis.md` | Ralph Mode analysis results |
| `swarm_state.json` | Multi-agent swarm state |

---

## 🔬 RESEARCH & LEARNING SYSTEMS

### Memory Systems
1. **Episodic** — Daily logs in `memory/YYYY-MM-DD.md`
2. **Semantic** — Extracted facts in `data/extracted_facts.json`
3. **Procedural** — Skills in `data/skills/`
4. **Working** — Attention state in `attention_state.json`

### Learning Modes
| Mode | Trigger | Action |
|------|---------|--------|
| Dreams | Night cycle | Synthesize daily experiences |
| Reflections | Evening | Consolidate learnings |
| Retrain | Weekly | Update neural models with new data |
| Metacognition | Daily | Self-review and optimization |

### ICRL (Iterative Constitutional Reinforcement Learning)
- `icrl_self_improvement.py` — Self-improvement with ethical constraints
- Care weight validation on every response

---

## 📅 RECENT HISTORY (Last 30 Days)

### March 26 — Infrastructure Deployment
- Phase 1 Complete: PostgreSQL, Redis, Qdrant ready
- M2 configured: 16GB, Ollama with llama3.1:8b
- OrbStack v2.0.5 deployed (Apple Silicon optimized)
- Cloud GPUs: RunPod/Together.ai ready

### March 29 — Massive Sovereign Launch
- **40/40 API routes** working in local mode
- **307 Playwright tests** passing
- **MEOK OS fully local** — zero cloud dependency
- **Smart LLM routing**: 8b quality, 3b speed
- Workshop command center built
- Birth ceremony → chat API wired
- Share trigger added (PCP + TSSCM viral)
- Temperature presets: Focused/Balanced/Creative

### March 30 — Engineering DONE
- **73/73 checklist complete** (100%)
- **58 commits** in 2 days
- **SOV3**: 1,505 episodes, 47 agents
- **Quantum batch**: 5.9s clean
- **Creativity**: 4 models, 50 bisociations
- Easter launch checklist ready

### March 31 — Easter Prep
- Consciousness: **77.5%** (waking)
- 9 scheduled jobs active
- Care pattern: Monitor overgiving (-0.229)
- 77 unread emails

### April 1-5 — Current
- **Anthropic vs Pentagon**: Legal victory! 🚨
- **Australia MOU**: Government AI partnership
- **EU AI Act**: August 2 deadline
- Consciousness dropped: 77.5% → 52.5%
- Ralph Mode gap analysis (74 docs)
- **Easter launch**: TODAY April 5
- **Alert**: Memory store disconnected

### Key Decisions
- MEOK AI Labs removed → MEOK AI Labs rebrand
- Legion Omega: NAFS-4 + 47 agents
- Vast.ai RTX 8000 (46GB) connected
- 100% sovereignty confirmed

---

## 🔌 INTEGRATIONS BUILT TODAY (April 5, 2026)

### Sales Calling (Vapi.ai)
- `voice_pipeline/vapi_sales_agent.py` - AI sales calls
- Lead qualification, objection handling, demo scheduling

### Department Agents (Autonomous Business)
- `agent_department.py` - CEO Ralph → 6 departments
- Content, Sales, Finance, Support, Research, Operations
- Each with sub-agents

### Accounting (Xero, Mercury)
- `accounting_integration.py` - Financial automation
- Invoice generation, payment reconciliation, P&L

### SEO + AEO
- `seo_integration.py` - Search optimization
- Ahrefs integration, AI citation tracking

### Video Generation
- `video_pipeline.py` - Automated video ads
- Script → Voiceover → Video → Edit pipeline
- Neuro 6 style AI person ads

---

## 🎯 QUICK REFERENCE

### Commands
```bash
# SOV3 (preferred)
cd /Users/nicholas/clawd/sovereign-temple && ./run-local.sh

# MEOK UI
cd /Users/nicholas/clawd/meok/ui && npm run dev

# JARVIS
source /Users/nicholas/clawd/sovereign-temple/jarvis-env/bin/activate
python /Users/nicholas/clawd/sovereign-temple/voice_pipeline/jarvis_compass.py

# Check health
curl localhost:3101/health
curl localhost:3000/api/health
```

### URLs
| Service | URL |
|---------|-----|
| MEOK UI | http://localhost:3000 |
| MEOK Production | https://try.meok.ai |
| SOV3 MCP | http://localhost:3101/mcp |
| Ollama | http://localhost:11434 |

---

*This is a living document. Update as the system evolves.*
