#!/usr/bin/env python3
"""
Sovereign Temple MCP Server
Complete implementation with all 5 expansion modules
"""

import asyncio
import json
import sys
import os
import subprocess
from datetime import datetime
from typing import Optional, Dict, Any, List
from contextlib import asynccontextmanager

# Add module paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'neural_core'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'rag_core'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'monitoring'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'multi_agent'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'consciousness'))

from fastapi import FastAPI, HTTPException, BackgroundTasks, Request, Response
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Import our modules
from neural_core import create_default_registry, NeuralModelRegistry
from alert_system import AlertManager, AlertSeverity, AlertChannel, console_alert_handler
from audit_logger import AuditLogger, AuditEventType
from metrics_collector import MetricsCollector
from enhanced_memory import EnhancedMemoryStore
from agent_registry import AgentRegistry, TaskDelegator, AgentCouncil, AgentCapability
from emotional_state import ConsciousnessOrchestrator
from autonomous_maintenance import AutonomousMaintenanceSystem

# Project Heartbeat — Autonomous Self-Improvement
try:
    from sovereign_heartbeat import SovereignHeartbeat
    HEARTBEAT_AVAILABLE = True
except ImportError:
    HEARTBEAT_AVAILABLE = False
    SovereignHeartbeat = None

try:
    from sovereign_research_agent import AutonomousResearchAgent
    RESEARCH_AVAILABLE = True
except ImportError:
    RESEARCH_AVAILABLE = False

try:
    from sovereign_security_hardening import SecurityHardeningEngine
    SECURITY_HARDENING_AVAILABLE = True
except ImportError:
    SECURITY_HARDENING_AVAILABLE = False

try:
    from sovereign_continual_learning import ContinualLearningTrainer
    CONTINUAL_LEARNING_AVAILABLE = True
except ImportError:
    CONTINUAL_LEARNING_AVAILABLE = False

# Civilizational Creativity Engine
try:
    from creativity_engine import (
        CreativityAssessmentNN, CreativityTrainingPipeline,
        kolmogorov_novelty, CORPUS, get_corpus_stats, ingest_corpus,
    )
    CREATIVITY_ENGINE_AVAILABLE = True
except ImportError:
    CREATIVITY_ENGINE_AVAILABLE = False
    CreativityTrainingPipeline = None

# Tier 2: Cross-Domain Bisociation, Stochastic Resonance, Quality-Diversity
try:
    from creativity_engine.cross_domain_linker import CrossDomainLinker
    from creativity_engine.stochastic_resonance import StochasticResonanceEngine, apply_stochastic_resonance
    from creativity_engine.quality_diversity import QualityDiversityArchive
    TIER2_CREATIVITY_AVAILABLE = True
except ImportError:
    TIER2_CREATIVITY_AVAILABLE = False
    CrossDomainLinker = None
    StochasticResonanceEngine = None
    QualityDiversityArchive = None

# Kimi Agent (Moonshot AI)
try:
    from creativity_engine.kimi_agent import KimiAgent
    KIMI_AVAILABLE = True
except ImportError:
    KIMI_AVAILABLE = False
    KimiAgent = None

# Orion-Riri-Hourman Agent
# Try bundled ext_agents first (inside Docker), fallback to sovereign-temple-live on host
_orion_paths = [
    os.path.join(os.path.dirname(__file__), 'ext_agents'),
    os.path.join(os.path.dirname(__file__), '..', 'sovereign-temple-live', 'agents'),
]
for _p in _orion_paths:
    if _p not in sys.path:
        sys.path.insert(0, _p)
try:
    from orion_riri_hourman import HunterBuilderAgent, get_agent as get_orion_agent
    ORION_AGENT_AVAILABLE = True
except ImportError as _e:
    print(f"[startup] Orion import failed: {_e}")
    ORION_AGENT_AVAILABLE = False
    get_orion_agent = None

# Multi-Agent Coordination Hub
# Try bundled ext_coordination first (inside Docker), fallback to sovereign-temple-live on host
_coord_paths = [
    os.path.join(os.path.dirname(__file__), 'ext_coordination'),
    os.path.join(os.path.dirname(__file__), '..', 'sovereign-temple-live', 'coordination'),
]
for _p in _coord_paths:
    if _p not in sys.path:
        sys.path.insert(0, _p)
try:
    from coordination import get_hub as get_coordination_hub
    COORDINATION_AVAILABLE = True
except ImportError as _e:
    print(f"[startup] Coordination import failed: {_e}")
    COORDINATION_AVAILABLE = False
    get_coordination_hub = None

# MCP Models
class ToolCall(BaseModel):
    name: str
    arguments: Dict[str, Any]

class McpRequest(BaseModel):
    jsonrpc: str = "2.0"
    id: Optional[str] = None
    method: str
    params: Optional[Dict[str, Any]] = None

# Global state
model_registry: Optional[NeuralModelRegistry] = None
memory_store: Optional[EnhancedMemoryStore] = None
audit_logger: Optional[AuditLogger] = None
metrics: Optional[MetricsCollector] = None
alert_manager: Optional[AlertManager] = None
agent_registry: Optional[AgentRegistry] = None
task_delegator: Optional[TaskDelegator] = None
agent_council: Optional[AgentCouncil] = None
consciousness: Optional[ConsciousnessOrchestrator] = None
maintenance_system: Optional[AutonomousMaintenanceSystem] = None
heartbeat: Optional[Any] = None  # SovereignHeartbeat instance
research_agent: Optional[Any] = None  # AutonomousResearchAgent instance
security_engine: Optional[Any] = None  # SecurityHardeningEngine instance
continual_trainer: Optional[Any] = None  # ContinualLearningTrainer instance
creativity_pipeline: Optional[Any] = None  # CreativityTrainingPipeline instance
cross_domain_linker: Optional[Any] = None  # CrossDomainLinker instance
resonance_engine: Optional[Any] = None  # StochasticResonanceEngine instance
qd_archive: Optional[Any] = None  # QualityDiversityArchive instance
kimi_agent: Optional[Any] = None  # KimiAgent when available
orion_agent: Optional[Any] = None  # HunterBuilderAgent when available
coordination_hub: Optional[Any] = None

# MCP Tools Definition
MCP_TOOLS = [
    # Neural Tools
    {
        "name": "validate_care",
        "description": "Validate text against care-centered principles using neural network",
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Text to validate"}
            },
            "required": ["text"]
        }
    },
    {
        "name": "detect_partnership_opportunities",
        "description": "Detect strategic partnership opportunities from text",
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Text to analyze"}
            },
            "required": ["text"]
        }
    },
    {
        "name": "detect_threats",
        "description": "Detect security threats, adversarial inputs, or manipulation attempts",
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Text to analyze for threats"}
            },
            "required": ["text"]
        }
    },
    {
        "name": "predict_relationship_evolution",
        "description": "Predict how a relationship will evolve over time",
        "inputSchema": {
            "type": "object",
            "properties": {
                "current_trust": {"type": "number"},
                "interaction_frequency": {"type": "number"},
                "care_score_avg": {"type": "number"},
                "conflict_count": {"type": "integer"},
                "collaboration_count": {"type": "integer"},
                "days_since_first_contact": {"type": "integer"},
                "reciprocity_score": {"type": "number"},
                "vulnerability_sharing": {"type": "number"},
                "boundary_respect": {"type": "number"},
                "shared_value_alignment": {"type": "number"}
            },
            "required": ["current_trust"]
        }
    },
    {
        "name": "analyze_care_patterns",
        "description": "Analyze care patterns to detect burnout or imbalance",
        "inputSchema": {
            "type": "object",
            "properties": {
                "care_given_per_day": {"type": "number"},
                "care_received_per_day": {"type": "number"},
                "active_relationships": {"type": "integer"},
                "high_demand_relationships": {"type": "integer"},
                "avg_care_quality": {"type": "number"},
                "days_since_self_care": {"type": "integer"},
                "boundary_violations": {"type": "integer"},
                "emotional_exhaustion_score": {"type": "number"},
                "relationship_satisfaction": {"type": "number"},
                "energy_level": {"type": "number"},
                "sleep_quality": {"type": "number"},
                "work_life_balance": {"type": "number"}
            },
            "required": ["care_given_per_day"]
        }
    },
    {
        "name": "get_neural_model_info",
        "description": "Get information about all neural models",
        "inputSchema": {"type": "object", "properties": {}}
    },
    
    # Memory Tools
    {
        "name": "record_memory",
        "description": "Record a memory episode with care-weighting",
        "inputSchema": {
            "type": "object",
            "properties": {
                "content": {"type": "string"},
                "source_agent": {"type": "string"},
                "memory_type": {"type": "string", "enum": ["interaction", "insight", "decision", "emotion"]},
                "care_weight": {"type": "number"},
                "tags": {"type": "array", "items": {"type": "string"}},
                "emotional_valence": {"type": "number"}
            },
            "required": ["content", "source_agent"]
        }
    },
    {
        "name": "query_memories",
        "description": "Query memories using semantic search with care-weighting",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "care_weight_min": {"type": "number"},
                "tags": {"type": "array", "items": {"type": "string"}},
                "limit": {"type": "integer"}
            },
            "required": ["query"]
        }
    },
    {
        "name": "get_temporal_chain",
        "description": "Get temporal chain of related memories",
        "inputSchema": {
            "type": "object",
            "properties": {
                "episode_id": {"type": "string"},
                "direction": {"type": "string", "enum": ["forward", "backward", "both"]},
                "max_steps": {"type": "integer"}
            },
            "required": ["episode_id"]
        }
    },
    {
        "name": "get_memory_stats",
        "description": "Get memory system statistics",
        "inputSchema": {"type": "object", "properties": {}}
    },
    {
        "name": "list_memories",
        "description": "List all memories from PostgreSQL",
        "inputSchema": {
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "description": "Maximum memories to return", "default": 50}
            }
        }
    },
    
    # Monitoring Tools
    {
        "name": "get_dashboard_metrics",
        "description": "Get real-time dashboard metrics",
        "inputSchema": {"type": "object", "properties": {}}
    },
    {
        "name": "get_audit_logs",
        "description": "Query audit logs",
        "inputSchema": {
            "type": "object",
            "properties": {
                "event_type": {"type": "string"},
                "source_agent": {"type": "string"},
                "limit": {"type": "integer"}
            }
        }
    },
    {
        "name": "get_active_alerts",
        "description": "Get active alerts",
        "inputSchema": {
            "type": "object",
            "properties": {
                "min_severity": {"type": "string", "enum": ["info", "warning", "critical", "emergency"]}
            }
        }
    },
    
    # Multi-Agent Tools
    {
        "name": "register_agent",
        "description": "Register a new agent",
        "inputSchema": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "description": {"type": "string"},
                "capabilities": {"type": "array", "items": {"type": "string"}},
                "trust_level": {"type": "number"}
            },
            "required": ["name", "capabilities"]
        }
    },
    {
        "name": "delegate_task",
        "description": "Delegate a task to the best available agent",
        "inputSchema": {
            "type": "object",
            "properties": {
                "description": {"type": "string"},
                "required_capabilities": {"type": "array", "items": {"type": "string"}},
                "priority": {"type": "integer"},
                "care_weight": {"type": "number"}
            },
            "required": ["description", "required_capabilities"]
        }
    },
    {
        "name": "submit_council_proposal",
        "description": "Submit a proposal for agent council vote",
        "inputSchema": {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "description": {"type": "string"},
                "proposed_by": {"type": "string"},
                "action_type": {"type": "string"},
                "action_params": {"type": "object"}
            },
            "required": ["title", "description", "proposed_by"]
        }
    },
    {
        "name": "vote_on_proposal",
        "description": "Cast a vote on a council proposal",
        "inputSchema": {
            "type": "object",
            "properties": {
                "proposal_id": {"type": "string"},
                "agent_id": {"type": "string"},
                "vote": {"type": "string", "enum": ["for", "against", "abstain"]},
                "reasoning": {"type": "string"}
            },
            "required": ["proposal_id", "agent_id", "vote"]
        }
    },
    {
        "name": "get_agent_registry_stats",
        "description": "Get agent registry statistics",
        "inputSchema": {"type": "object", "properties": {}}
    },
    
    # Consciousness Tools
    {
        "name": "get_consciousness_state",
        "description": "Get current consciousness state including emotions",
        "inputSchema": {"type": "object", "properties": {}}
    },
    {
        "name": "trigger_reflection",
        "description": "Trigger a reflection cycle",
        "inputSchema": {
            "type": "object",
            "properties": {
                "trigger": {"type": "string"}
            }
        }
    },
    {
        "name": "enter_dream_state",
        "description": "Enter dream state for background processing",
        "inputSchema": {
            "type": "object",
            "properties": {
                "duration_seconds": {"type": "integer"}
            }
        }
    },
    
    # System Tools
    {
        "name": "sovereign_health_check",
        "description": "Check overall system health",
        "inputSchema": {"type": "object", "properties": {}}
    },
    {
        "name": "get_system_status",
        "description": "Get complete system status",
        "inputSchema": {"type": "object", "properties": {}}
    },
    {
        "name": "trigger_maintenance",
        "description": "Manually trigger autonomous maintenance cycle",
        "inputSchema": {"type": "object", "properties": {}}
    },
    {
        "name": "get_maintenance_status",
        "description": "Get autonomous maintenance system status",
        "inputSchema": {"type": "object", "properties": {}}
    },
    
    # Orion-Riri-Hourman Agent Tools
    {
        "name": "orion_hunt_tasks",
        "description": "Hunt for TODO/FIXME tasks across the codebase (Orion module)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "max_files": {"type": "integer", "description": "Max files to scan", "default": 100}
            }
        }
    },
    {
        "name": "orion_get_tasks",
        "description": "Get prioritized tasks ready for capture",
        "inputSchema": {
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "description": "Number of tasks to return", "default": 10}
            }
        }
    },
    {
        "name": "orion_capture_task",
        "description": "Capture a task for sprint execution",
        "inputSchema": {
            "type": "object",
            "properties": {
                "task_id": {"type": "string", "description": "Task ID to capture"}
            },
            "required": ["task_id"]
        }
    },
    {
        "name": "hourman_start_sprint",
        "description": "Start a Miraclo sprint (micro/power/deep)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "sprint_type": {"type": "string", "enum": ["micro", "power", "deep"], "description": "Sprint duration type"},
                "task_id": {"type": "string", "description": "Optional task ID to focus on"}
            },
            "required": ["sprint_type"]
        }
    },
    {
        "name": "hourman_get_status",
        "description": "Get sprint controller status and energy levels",
        "inputSchema": {"type": "object", "properties": {}}
    },
    {
        "name": "hourman_complete_sprint",
        "description": "Complete the active sprint with results",
        "inputSchema": {
            "type": "object",
            "properties": {
                "summary": {"type": "string", "description": "Summary of what was accomplished"},
                "task_id": {"type": "string", "description": "Optional task ID to mark complete"}
            },
            "required": ["summary"]
        }
    },
    {
        "name": "riri_list_templates",
        "description": "List available tool templates for rapid building",
        "inputSchema": {"type": "object", "properties": {}}
    },
    {
        "name": "riri_build_tool",
        "description": "Build a tool from a template (Riri module)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "template": {"type": "string", "description": "Template name"},
                "name": {"type": "string", "description": "Tool name"},
                "description": {"type": "string", "description": "Tool description"},
                "params": {"type": "object", "description": "Template-specific parameters"}
            },
            "required": ["template", "name", "description"]
        }
    },
    {
        "name": "orion_riri_hourman_status",
        "description": "Get complete Orion-Riri-Hourman agent status",
        "inputSchema": {"type": "object", "properties": {}}
    },
    
    # Multi-Agent Coordination Tools
    {
        "name": "coord_register_agent",
        "description": "Register an agent with the coordination hub",
        "inputSchema": {
            "type": "object",
            "properties": {
                "agent_id": {"type": "string"},
                "agent_type": {"type": "string", "enum": ["claude-desktop", "claude-code", "kimi-cli", "orion-agent", "openhands"]},
                "capabilities": {"type": "array", "items": {"type": "string"}}
            },
            "required": ["agent_id", "agent_type", "capabilities"]
        }
    },
    {
        "name": "coord_submit_task",
        "description": "Submit a task to the coordination queue",
        "inputSchema": {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "description": {"type": "string"},
                "files": {"type": "array", "items": {"type": "string"}},
                "care_score": {"type": "number", "minimum": 0, "maximum": 1}
            },
            "required": ["title", "description", "files"]
        }
    },
    {
        "name": "coord_acquire_files",
        "description": "Acquire files for editing (with locking)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "agent_id": {"type": "string"},
                "files": {"type": "array", "items": {"type": "string"}},
                "task_id": {"type": "string"},
                "exclusive": {"type": "boolean", "default": False}
            },
            "required": ["agent_id", "files", "task_id"]
        }
    },
    {
        "name": "coord_release_files",
        "description": "Release file locks",
        "inputSchema": {
            "type": "object",
            "properties": {
                "agent_id": {"type": "string"},
                "files": {"type": "array", "items": {"type": "string"}}
            },
            "required": ["agent_id", "files"]
        }
    },
    {
        "name": "coord_complete_task",
        "description": "Mark a task as complete",
        "inputSchema": {
            "type": "object",
            "properties": {
                "task_id": {"type": "string"},
                "agent_id": {"type": "string"},
                "result_summary": {"type": "string"},
                "care_score": {"type": "number"}
            },
            "required": ["task_id", "agent_id", "result_summary"]
        }
    },
    {
        "name": "coord_get_dashboard",
        "description": "Get coordination dashboard with all agents and tasks",
        "inputSchema": {"type": "object", "properties": {}}
    },
    # Project Heartbeat — Autonomous Self-Improvement Tools
    {
        "name": "get_heartbeat_status",
        "description": "Get Sovereign heartbeat scheduler status, running jobs, and next run times",
        "inputSchema": {"type": "object", "properties": {}}
    },
    {
        "name": "get_nightshift_digest",
        "description": "Get the latest morning intelligence digest compiled during nightshift",
        "inputSchema": {"type": "object", "properties": {}}
    },
    {
        "name": "trigger_research_sweep",
        "description": "Manually trigger an autonomous research sweep (RSS + web + Ollama summarization)",
        "inputSchema": {"type": "object", "properties": {}}
    },
    {
        "name": "trigger_security_hardening",
        "description": "Manually trigger a security self-hardening cycle",
        "inputSchema": {"type": "object", "properties": {}}
    },
    {
        "name": "trigger_neural_retrain",
        "description": "Manually trigger neural model retraining cycle",
        "inputSchema": {"type": "object", "properties": {}}
    },
    {
        "name": "pause_heartbeat_job",
        "description": "Pause a specific heartbeat scheduler job (human override)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "job_id": {"type": "string", "description": "Job ID to pause (e.g., heartbeat_pulse, nightshift_deep, research_sweep)"}
            },
            "required": ["job_id"]
        }
    },
    {
        "name": "resume_heartbeat_job",
        "description": "Resume a paused heartbeat scheduler job",
        "inputSchema": {
            "type": "object",
            "properties": {
                "job_id": {"type": "string", "description": "Job ID to resume"}
            },
            "required": ["job_id"]
        }
    },
    # Civilizational Creativity Engine Tools
    {
        "name": "ingest_civilizational_knowledge",
        "description": "Ingest the 47-tradition civilizational knowledge corpus into memory. Idempotent — safe to call multiple times.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "force": {"type": "boolean", "description": "Force re-ingestion even if already present", "default": False}
            }
        }
    },
    {
        "name": "assess_creativity",
        "description": "Assess creative quality of content using the CreativityAssessmentNN trained on 47 civilizational traditions",
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Content to assess for creativity"},
                "novelty_score": {"type": "number", "description": "Pre-computed novelty score (0-1)"},
                "domain_distance": {"type": "number", "description": "Cross-domain distance (0-1)"},
                "care_alignment": {"type": "number", "description": "Care principle alignment (0-1)"}
            },
            "required": ["text"]
        }
    },
    {
        "name": "get_asabiyyah_score",
        "description": "Get Ibn Khaldun's asabiyyah (group cohesion) metric for the agent ecosystem",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "get_consciousness_mode",
        "description": "Get the current Vedantic consciousness mode: Jagrat (waking), Svapna (dreaming), Susupti (deep sleep), or Turiya (meta-monitoring)",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "compute_novelty",
        "description": "Compute Kolmogorov complexity novelty score for text against reference corpus",
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Text to score for novelty"},
                "reference_texts": {"type": "array", "items": {"type": "string"}, "description": "Reference corpus (optional — uses recent memories if empty)"}
            },
            "required": ["text"]
        }
    },
    {
        "name": "trigger_creativity_cycle",
        "description": "Manually trigger the creativity nightshift cycle: Susupti consolidation → NREM/REM dreaming → novelty scoring → creative assessment",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "get_meta_observations",
        "description": "Get Turiya meta-monitor observations — meta-cognitive assessment of system coherence across all subsystems",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    },
    # Tier 2: Cross-Domain Bisociation
    {
        "name": "find_bisociations",
        "description": "Find surprising cross-domain connections between civilizational traditions (Koestler bisociation). Returns ranked creative collision opportunities.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "min_distance": {"type": "number", "description": "Minimum semantic distance threshold (0-1, default 0.4)"},
                "top_k": {"type": "integer", "description": "Number of top links to return (default 15)"}
            }
        }
    },
    {
        "name": "get_dream_targets",
        "description": "Get suggested tradition pairs for REM dream creative recombination. Weighted random selection from top bisociation links.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "n": {"type": "integer", "description": "Number of dream targets (default 5)"}
            }
        }
    },
    {
        "name": "get_bridge_concepts",
        "description": "Rank traditions by cross-domain connectivity. Bridge concepts connect many disparate domains and are especially valuable for creative synthesis.",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    },
    # Tier 2: Stochastic Resonance
    {
        "name": "apply_resonance",
        "description": "Apply stochastic resonance noise to creativity features. Amplifies weak creative signals through optimal noise injection.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "features": {"type": "object", "description": "Feature dict (novelty_score, domain_distance, care_alignment, etc.)"},
                "temperature": {"type": "number", "description": "Noise scaling (>1 more noise, <1 less, default auto)"}
            },
            "required": ["features"]
        }
    },
    {
        "name": "get_resonance_profile",
        "description": "Get the current noise resonance profile — per-feature sigma values and optimal temperature.",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    },
    # Tier 2: Quality-Diversity Archive
    {
        "name": "get_qd_archive_stats",
        "description": "Get MAP-Elites quality-diversity archive statistics — coverage, quality distribution, domain breakdown.",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "get_empty_niches",
        "description": "Find unexplored creative territory in the MAP-Elites archive. Returns empty cells = domains × novelty levels × care levels not yet explored.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "description": "Max niches to return (default 20)"}
            }
        }
    },
    {
        "name": "suggest_exploration",
        "description": "Suggest creative directions that would fill empty niches in the quality-diversity archive. Prioritizes niches near existing high-quality outputs.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "n": {"type": "integer", "description": "Number of suggestions (default 5)"}
            }
        }
    },
    {
        "name": "get_domain_distances",
        "description": "Get average semantic distance between each pair of civilizational domains. Shows which domains are most/least related.",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    },
    # Kimi Agent
    {
        "name": "kimi_send_task",
        "description": "Send a task to Kimi (Moonshot AI) — general-purpose code/analysis tasks",
        "inputSchema": {
            "type": "object",
            "properties": {
                "task": {"type": "string", "description": "Task description"},
                "context": {"type": "string", "description": "Additional context (code, specs)"},
                "model": {"type": "string", "description": "Model: 8k, 32k, or 128k (default 32k)"}
            },
            "required": ["task"]
        }
    },
    {
        "name": "kimi_build_frontend",
        "description": "Delegate a frontend build task to Kimi — React, TypeScript, Next.js specialist",
        "inputSchema": {
            "type": "object",
            "properties": {
                "spec": {"type": "string", "description": "What to build"},
                "framework": {"type": "string", "description": "Framework (default: Next.js + TypeScript)"},
                "files": {"type": "object", "description": "Existing files as {filename: content}"}
            },
            "required": ["spec"]
        }
    },
    {
        "name": "kimi_review_code",
        "description": "Send code to Kimi for review — bugs, performance, accessibility",
        "inputSchema": {
            "type": "object",
            "properties": {
                "code": {"type": "string", "description": "Code to review"},
                "language": {"type": "string", "description": "Language (default: typescript)"},
                "focus": {"type": "string", "description": "Review focus areas"}
            },
            "required": ["code"]
        }
    },
    {
        "name": "kimi_status",
        "description": "Get Kimi agent status — connection, task history, success rate",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "kimi_list_models",
        "description": "List available Kimi (Moonshot AI) models",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    },
    # Sovereign Rundown
    {
        "name": "sovereign_rundown",
        "description": "Comprehensive system rundown — all subsystems, agents, creativity engine, memory, consciousness state in one call",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    }
]

async def initialize_system():
    """Initialize all subsystems"""
    global model_registry, memory_store, audit_logger, metrics, alert_manager
    global agent_registry, task_delegator, agent_council, consciousness, maintenance_system
    
    print("🚀 Initializing Sovereign Temple MCP Server...")
    
    # Initialize neural models
    print("  📊 Loading neural models...")
    model_registry = create_default_registry(model_dir="models")
    
    # Try to load existing models, train if not available
    for name, model in model_registry.models.items():
        if not model.load_model():
            print(f"    Training {name}...")
            model.train_model()
            model.save_model()
        else:
            print(f"    Loaded {name}")
    
    # Initialize memory store
    print("  💾 Initializing memory store...")
    postgres_dsn = os.environ.get("POSTGRES_DSN", "postgresql://sovereign:sovereign@postgres:5432/sovereign_memory")
    weaviate_url = os.environ.get("WEAVIATE_URL", "http://weaviate:8080")
    memory_store = EnhancedMemoryStore(postgres_dsn=postgres_dsn, weaviate_url=weaviate_url)
    try:
        await memory_store.initialize()
        print("    Memory store ready")
    except Exception as e:
        print(f"    Memory store initialization failed (will retry): {e}")
    
    # Initialize monitoring
    print("  📡 Initializing monitoring...")
    postgres_dsn = os.environ.get("POSTGRES_DSN", "postgresql://sovereign:sovereign@localhost:5432/sovereign_memory")
    audit_logger = AuditLogger(postgres_dsn=postgres_dsn)
    try:
        await audit_logger.initialize()
        print("    Audit logger ready")
    except Exception as e:
        print(f"    Audit logger initialization failed: {e}")
    
    metrics = MetricsCollector()
    await metrics.start_collection()
    print("    Metrics collection started")
    
    alert_manager = AlertManager()
    alert_manager.add_handler(AlertChannel.CONSOLE, console_alert_handler)
    alert_manager.setup_default_rules()
    print("    Alert manager ready")
    
    # Initialize multi-agent system
    print("  🤖 Initializing multi-agent system...")
    agent_registry = AgentRegistry(postgres_dsn=postgres_dsn)
    try:
        await agent_registry.initialize()
        print("    Agent registry ready")
    except Exception as e:
        print(f"    Agent registry initialization failed: {e}")
    
    task_delegator = TaskDelegator(agent_registry)
    agent_council = AgentCouncil(agent_registry)
    print("    Task delegation ready")
    
    # Initialize consciousness
    print("  🧠 Initializing consciousness module...")
    consciousness = ConsciousnessOrchestrator(memory_store)
    await consciousness.initialize()
    print("    Consciousness module ready")
    
    # Initialize autonomous maintenance
    print("  🔄 Initializing autonomous maintenance...")
    maintenance_system = AutonomousMaintenanceSystem(memory_store, consciousness)
    await maintenance_system.start()
    print("    Autonomous maintenance running (care floor: 0.3)")
    
    # Initialize Project Heartbeat — autonomous self-improvement scheduler
    global heartbeat, research_agent, security_engine, continual_trainer
    if HEARTBEAT_AVAILABLE:
        print("  💓 Initializing Project Heartbeat...")
        try:
            heartbeat = SovereignHeartbeat(
                memory_store=memory_store,
                consciousness=consciousness,
                maintenance_system=maintenance_system,
                alert_manager=alert_manager,
                model_registry=model_registry,
                agent_registry=agent_registry,
                metrics=metrics
            )
            heartbeat.start()
            print("    Heartbeat scheduler running — Sovereign is alive 24/7")
        except Exception as e:
            print(f"    Heartbeat initialization failed: {e}")

    if RESEARCH_AVAILABLE:
        try:
            research_agent = AutonomousResearchAgent(memory_store)
            print("    Research agent ready")
        except Exception as e:
            print(f"    Research agent init failed: {e}")

    if SECURITY_HARDENING_AVAILABLE:
        try:
            security_engine = SecurityHardeningEngine(
                model_registry=model_registry,
                agent_registry=agent_registry,
                alert_manager=alert_manager,
                memory_store=memory_store,
                audit_logger=audit_logger
            )
            print("    Security hardening engine ready")
        except Exception as e:
            print(f"    Security hardening init failed: {e}")

    if CONTINUAL_LEARNING_AVAILABLE:
        try:
            continual_trainer = ContinualLearningTrainer(model_registry, memory_store)
            print("    Continual learning trainer ready")
        except Exception as e:
            print(f"    Continual learning init failed: {e}")

    # Initialize Civilizational Creativity Engine
    global creativity_pipeline
    if CREATIVITY_ENGINE_AVAILABLE:
        print("  🎨 Initializing Creativity Engine...")
        try:
            creativity_pipeline = CreativityTrainingPipeline(
                model_registry=model_registry,
                memory_store=memory_store,
                ewc_regularizer=continual_trainer,
            )
            # Train creativity model on first boot
            creativity_result = await creativity_pipeline.train_creativity_model()
            print(f"    CreativityAssessmentNN trained (MSE: {creativity_result.get('metrics', {}).get('mse', '?')})")

            # Ingest civilizational corpus into memory (idempotent)
            corpus_result = await ingest_corpus(memory_store)
            if corpus_result.get("status") == "complete":
                print(f"    Civilizational corpus ingested: {corpus_result.get('traditions_ingested', 0)} traditions")
            elif corpus_result.get("status") == "already_ingested":
                print("    Civilizational corpus already in memory")
            else:
                print(f"    Corpus ingestion: {corpus_result.get('status', 'unknown')}")
        except Exception as e:
            print(f"    Creativity engine init failed: {e}")

    # Initialize Tier 2: Cross-Domain Bisociation, Stochastic Resonance, QD Archive
    global cross_domain_linker, resonance_engine, qd_archive
    if TIER2_CREATIVITY_AVAILABLE:
        print("  🧬 Initializing Tier 2 Creativity Systems...")
        try:
            # Cross-domain bisociation linker
            cross_domain_linker = CrossDomainLinker()
            cross_domain_linker.compute_distances()
            cross_domain_linker.find_bisociations(top_k=30)
            stats = cross_domain_linker.get_stats()
            print(f"    CrossDomainLinker: {stats.get('total_links', 0)} bisociation links found")

            # Stochastic resonance engine
            resonance_engine = StochasticResonanceEngine(n_features=12)
            print(f"    StochasticResonance: σ={resonance_engine.get_stats()['mean_sigma']}")

            # Quality-Diversity archive (MAP-Elites)
            qd_archive = QualityDiversityArchive()
            print(f"    QD Archive: {qd_archive.total_cells} cells ({qd_archive.grid_shape})")
        except Exception as e:
            print(f"    Tier 2 creativity init failed: {e}")

    # Initialize Kimi Agent
    global kimi_agent
    kimi_key = os.environ.get("KIMI_API_KEY", "")
    if kimi_key and KIMI_AVAILABLE:
        print("  🤖 Initializing Kimi Agent...")
        try:
            kimi_agent = KimiAgent(api_key=kimi_key)
            print(f"    Kimi connected (model: {kimi_agent.default_model})")
            # Register in agent registry if available
            if agent_registry:
                try:
                    await agent_registry.register_agent(
                        name="Kimi",
                        description="Moonshot AI code agent — frontend builds, TypeScript, React",
                        capabilities=[AgentCapability.CODE_EXECUTION, AgentCapability.CREATIVE, AgentCapability.ANALYSIS],
                        trust_level=0.7,
                        metadata={"type": "external_api", "provider": "moonshot", "model": "moonshot-v1-32k"}
                    )
                    print("    Kimi registered in agent registry")
                except Exception as e:
                    print(f"    Kimi registry failed (non-fatal): {e}")
        except Exception as e:
            print(f"    Kimi init failed: {e}")

    # === BUG 3 FIX: Eagerly initialize Coordination Hub ===
    global coordination_hub
    if COORDINATION_AVAILABLE and get_coordination_hub:
        print("  🔗 Initializing Coordination Hub (eager)...")
        try:
            coordination_hub = get_coordination_hub()
            # Force state_dir creation so the hub is confirmed live
            coordination_hub.state_dir.mkdir(parents=True, exist_ok=True)
            print(f"    Coordination hub ready (state_dir: {coordination_hub.state_dir})")
        except Exception as e:
            print(f"    Coordination hub init failed (logged): {e}")
            coordination_hub = None
    else:
        print("  ⚠️  Coordination hub import failed — coordination_available: false")

    # === BUG 4 FIX: Eagerly initialize Orion-Riri-Hourman Agent ===
    global orion_agent
    if ORION_AGENT_AVAILABLE and get_orion_agent:
        print("  🎯 Initializing Orion-Riri-Hourman Agent (eager)...")
        try:
            orion_agent = get_orion_agent()
            status = orion_agent.get_full_status()
            print(f"    Orion agent ready (tasks: {status.get('orion', {}).get('total_tasks', 0)})")
        except Exception as e:
            print(f"    Orion agent init failed (logged): {e}")
            orion_agent = None
    else:
        print("  ⚠️  Orion agent import failed — orion_available: false")

    # === BUG 7 FIX: Seed inter-agent relationships ===
    if agent_registry and len(agent_registry.agents) > 0:
        print("  🤝 Seeding agent relationships...")
        agent_ids = list(agent_registry.agents.keys())
        seeded = 0
        try:
            for i, aid in enumerate(agent_ids):
                # Give each agent relationships with up to 3 others (bidirectional)
                partners = [agent_ids[j] for j in range(len(agent_ids)) if j != i][:3]
                for partner_id in partners:
                    agent = agent_registry.agents[aid]
                    import json as _json
                    rels = agent.relationships if isinstance(agent.relationships, dict) else {}
                    if partner_id not in rels:
                        await agent_registry.update_relationship(aid, partner_id, 0.5)
                        seeded += 1
            print(f"    Seeded {seeded} inter-agent relationships")
        except Exception as e:
            print(f"    Relationship seeding failed (non-fatal): {e}")

    print("✅ Sovereign Temple initialized successfully!")

# Create FastAPI app
app = FastAPI(title="Sovereign Temple MCP Server", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    await initialize_system()

# === BUG 2 FIX: Production inference counter ===
_production_calls_today: int = 0
_production_calls_date: str = ""


def _increment_production_calls():
    """Increment production inference counter, resetting daily."""
    global _production_calls_today, _production_calls_date
    today = datetime.now().strftime("%Y-%m-%d")
    if today != _production_calls_date:
        _production_calls_today = 0
        _production_calls_date = today
    _production_calls_today += 1


async def _run_production_inference(message_text: str):
    """
    BUG 2 FIX: Run production neural inference on every incoming user message.
    - Threat detection (proactive, every message)
    - Care pattern analysis (if stress/burnout signals present)
    - Memory query (retrieve relevant context)
    - Metrics increment
    """
    global _production_calls_today
    _increment_production_calls()

    # 1. Threat detection on every message
    threat_result = None
    if model_registry:
        threat_model = model_registry.get("threat_detection_nn")
        if threat_model and threat_model.is_trained:
            try:
                threat_result = threat_model.predict(message_text)
                if metrics:
                    metrics.increment_counter("neural_predictions_total", labels={"provider": "threat_detection_nn"})
                if threat_result.get("threat_detected") and alert_manager:
                    await alert_manager.fire_alert(
                        AlertSeverity.CRITICAL,
                        "security",
                        "Production Threat Detected",
                        f"Level: {threat_result.get('overall_threat_level')}",
                        channels=[AlertChannel.CONSOLE]
                    )
            except Exception as e:
                print(f"[production_inference] threat detection error: {e}")

    # 2. Care pattern analysis if stress/burnout signals present
    stress_keywords = ["burnout", "exhausted", "overwhelmed", "stressed", "anxious", "can't cope", "too much", "struggling"]
    if any(kw in message_text.lower() for kw in stress_keywords):
        if model_registry:
            care_model = model_registry.get("care_pattern_analyzer")
            if care_model and care_model.is_trained:
                try:
                    care_result = care_model.predict({"care_given_per_day": 5, "care_received_per_day": 1})
                    if metrics:
                        metrics.increment_counter("neural_predictions_total", labels={"provider": "care_pattern_analyzer"})
                except Exception as e:
                    print(f"[production_inference] care pattern error: {e}")

    # 3. Memory query for relevant context
    if memory_store:
        try:
            await memory_store.query_memories(query=message_text[:200], care_weight_min=0.2, limit=3)
        except Exception as e:
            print(f"[production_inference] memory query error: {e}")

    # 4. Validate care on significant messages (longer messages imply meaningful interaction)
    if model_registry and len(message_text) > 50:
        care_val_model = model_registry.get("care_validation_nn")
        if care_val_model and care_val_model.is_trained:
            try:
                care_val_model.predict(message_text)
                if metrics:
                    metrics.increment_counter("neural_predictions_total", labels={"provider": "care_validation_nn"})
            except Exception as e:
                print(f"[production_inference] validate_care error: {e}")

    return threat_result


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    coord_status = "available" if (COORDINATION_AVAILABLE and coordination_hub is not None) else "unavailable"
    orion_status = "available" if (ORION_AGENT_AVAILABLE and orion_agent is not None) else "unavailable"
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0",
        "production_calls_today": _production_calls_today,
        "components": {
            "neural_models": model_registry.list_models() if model_registry else {},
            "memory_store": "connected" if memory_store else "disconnected",
            "consciousness": consciousness.get_consciousness_state() if consciousness else {},
            "coordination": coord_status,
            "orion_agent": orion_status,
        }
    }

@app.post("/mcp")
async def mcp_endpoint(request: Request):
    """MCP endpoint for tool calls"""
    body = await request.json()
    
    method = body.get("method")
    params = body.get("params", {})
    req_id = body.get("id")
    
    # Handle initialize
    if method == "initialize":
        return JSONResponse({
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "serverInfo": {
                    "name": "sovereign-temple-mcp",
                    "version": "2.0.0"
                },
                "capabilities": {
                    "tools": {}
                }
            }
        })
    
    # Handle tools/list
    if method == "tools/list":
        return JSONResponse({
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {"tools": MCP_TOOLS}
        })
    
    # Handle tools/call
    if method == "tools/call":
        tool_name = params.get("name")
        arguments = params.get("arguments", {})

        # BUG 2 FIX: Run production inference on every message that has text content
        message_text = arguments.get("text") or arguments.get("message") or arguments.get("content") or ""
        if message_text:
            asyncio.create_task(_run_production_inference(str(message_text)))

        result = await execute_tool(tool_name, arguments)
        
        return JSONResponse({
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "content": [{
                    "type": "text",
                    "text": json.dumps(result, indent=2)
                }]
            }
        })
    
    return JSONResponse({
        "jsonrpc": "2.0",
        "id": req_id,
        "error": {"code": -32601, "message": f"Method not found: {method}"}
    })

async def execute_tool(name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Execute an MCP tool"""
    start_time = datetime.now()
    
    try:
        # Neural Tools
        if name == "validate_care":
            model = model_registry.get("care_validation_nn")
            if not model or not model.is_trained:
                return {"error": "Model not available"}
            result = model.predict(arguments["text"])
            
            # Update consciousness
            consciousness.process_interaction({"care_score": result.get("overall_care_score", 0.5)})
            return result
        
        elif name == "detect_partnership_opportunities":
            model = model_registry.get("partnership_detection_ml")
            if not model or not model.is_trained:
                return {"error": "Model not available"}
            return model.predict(arguments["text"])
        
        elif name == "detect_threats":
            model = model_registry.get("threat_detection_nn")
            if not model or not model.is_trained:
                return {"error": "Model not available"}
            result = model.predict(arguments["text"])
            
            # Update consciousness
            consciousness.process_interaction({"threat_detected": result.get("threat_detected", False)})
            
            # Fire alert if threat detected
            if result.get("threat_detected"):
                await alert_manager.fire_alert(
                    AlertSeverity.CRITICAL,
                    "security",
                    "Security Threat Detected",
                    f"Threat level: {result.get('overall_threat_level', 'unknown')}",
                    channels=[AlertChannel.CONSOLE]
                )
            return result
        
        elif name == "predict_relationship_evolution":
            model = model_registry.get("relationship_evolution_nn")
            if not model or not model.is_trained:
                return {"error": "Model not available"}
            return model.predict(arguments)
        
        elif name == "analyze_care_patterns":
            model = model_registry.get("care_pattern_analyzer")
            if not model or not model.is_trained:
                return {"error": "Model not available"}
            return model.predict(arguments)
        
        elif name == "get_neural_model_info":
            return model_registry.list_models()
        
        # Memory Tools
        elif name == "record_memory":
            if not memory_store:
                return {"error": "Memory store not available"}
            episode = await memory_store.record_episode(
                content=arguments["content"],
                source_agent=arguments["source_agent"],
                memory_type=arguments.get("memory_type", "interaction"),
                care_weight=arguments.get("care_weight", 0.5),
                tags=arguments.get("tags", []),
                emotional_valence=arguments.get("emotional_valence", 0.5)
            )
            return {"success": True, "episode_id": episode.id}
        
        elif name == "query_memories":
            if not memory_store:
                return {"error": "Memory store not available"}
            results = await memory_store.query_memories(
                query=arguments["query"],
                care_weight_min=arguments.get("care_weight_min", 0.0),
                tags=arguments.get("tags"),
                limit=arguments.get("limit", 5)
            )
            return {"memories": results}
        
        elif name == "get_temporal_chain":
            if not memory_store:
                return {"error": "Memory store not available"}
            chain = await memory_store.get_temporal_chain(
                episode_id=arguments["episode_id"],
                direction=arguments.get("direction", "forward"),
                max_steps=arguments.get("max_steps", 5)
            )
            return {"chain": chain}
        
        elif name == "get_memory_stats":
            if not memory_store:
                return {"error": "Memory store not available"}
            return await memory_store.get_stats()
        
        elif name == "list_memories":
            if not memory_store:
                return {"error": "Memory store not available"}
            memories = await memory_store.list_all_memories(
                limit=arguments.get("limit", 50)
            )
            return {"memories": memories, "count": len(memories)}
        
        # Monitoring Tools
        elif name == "get_dashboard_metrics":
            return metrics.get_dashboard_data() if metrics else {"error": "Metrics not available"}
        
        elif name == "get_audit_logs":
            if not audit_logger:
                return {"error": "Audit logger not available"}
            logs = await audit_logger.query_logs(
                event_type=arguments.get("event_type"),
                source_agent=arguments.get("source_agent"),
                limit=arguments.get("limit", 100)
            )
            return {"logs": logs}
        
        elif name == "get_active_alerts":
            if not alert_manager:
                return {"error": "Alert manager not available"}
            severity_map = {
                "info": AlertSeverity.INFO,
                "warning": AlertSeverity.WARNING,
                "critical": AlertSeverity.CRITICAL,
                "emergency": AlertSeverity.EMERGENCY
            }
            min_sev = severity_map.get(arguments.get("min_severity"))
            alerts = alert_manager.get_active_alerts(min_severity=min_sev)
            return {
                "alerts": [{
                    "id": a.id,
                    "severity": a.severity.value,
                    "title": a.title,
                    "message": a.message,
                    "timestamp": a.timestamp.isoformat()
                } for a in alerts]
            }
        
        # Multi-Agent Tools
        elif name == "register_agent":
            if not agent_registry:
                return {"error": "Agent registry not available"}
            agent = await agent_registry.register_agent(
                name=arguments["name"],
                description=arguments.get("description", ""),
                capabilities=[AgentCapability(c) for c in arguments["capabilities"]],
                trust_level=arguments.get("trust_level", 0.5)
            )
            return {"agent_id": agent.id, "name": agent.name, "status": "registered"}
        
        elif name == "delegate_task":
            if not task_delegator:
                return {"error": "Task delegator not available"}
            task = await task_delegator.delegate_task(
                description=arguments["description"],
                required_capabilities=[AgentCapability(c) for c in arguments["required_capabilities"]],
                priority=arguments.get("priority", 5),
                care_weight=arguments.get("care_weight", 0.5)
            )
            if task:
                return {"task_id": task.id, "assigned_to": task.assigned_to, "status": "assigned"}
            return {"error": "No suitable agent found"}
        
        elif name == "submit_council_proposal":
            if not agent_council:
                return {"error": "Agent council not available"}
            proposal_id = await agent_council.submit_proposal(
                title=arguments["title"],
                description=arguments["description"],
                proposed_by=arguments["proposed_by"],
                action_type=arguments.get("action_type", "generic"),
                action_params=arguments.get("action_params", {})
            )
            return {"proposal_id": proposal_id, "status": "open"}
        
        elif name == "vote_on_proposal":
            if not agent_council:
                return {"error": "Agent council not available"}
            success = await agent_council.cast_vote(
                proposal_id=arguments["proposal_id"],
                agent_id=arguments["agent_id"],
                vote=arguments["vote"],
                reasoning=arguments.get("reasoning", "")
            )
            return {"success": success}
        
        elif name == "get_agent_registry_stats":
            if not agent_registry:
                return {"error": "Agent registry not available"}
            return agent_registry.get_registry_stats()
        
        # Consciousness Tools
        elif name == "get_consciousness_state":
            if not consciousness:
                return {"error": "Consciousness module not available"}
            return consciousness.get_consciousness_state()
        
        elif name == "trigger_reflection":
            if not consciousness:
                return {"error": "Consciousness module not available"}
            reflection = await consciousness.reflection.perform_reflection(
                trigger=arguments.get("trigger", "manual")
            )
            return reflection
        
        elif name == "enter_dream_state":
            if not consciousness:
                return {"error": "Consciousness module not available"}
            dream = await consciousness.dream.enter_dream_state(
                duration_seconds=arguments.get("duration_seconds", 30)
            )
            return dream
        
        # System Tools
        elif name == "sovereign_health_check":
            return {
                "status": "healthy",
                "components": {
                    "neural_models": len(model_registry.models) if model_registry else 0,
                    "memory_store": "connected" if memory_store else "disconnected",
                    "audit_logger": "connected" if audit_logger else "disconnected",
                    "metrics": "active" if metrics else "inactive",
                    "alert_manager": "active" if alert_manager else "inactive",
                    "agent_registry": "connected" if agent_registry else "disconnected",
                    "consciousness": "active" if consciousness else "inactive"
                }
            }
        
        elif name == "get_system_status":
            return {
                "neural": model_registry.list_models() if model_registry else {},
                "memory": await memory_store.get_stats() if memory_store else {},
                "monitoring": {
                    "alerts": alert_manager.get_alert_stats() if alert_manager else {},
                    "metrics": metrics.get_dashboard_data() if metrics else {}
                },
                "agents": agent_registry.get_registry_stats() if agent_registry else {},
                "consciousness": consciousness.get_consciousness_state() if consciousness else {},
                "maintenance": {
                    "running": maintenance_system.running if maintenance_system else False,
                    "care_floor": maintenance_system.care_floor if maintenance_system else None
                }
            }
        
        elif name == "trigger_maintenance":
            if not maintenance_system:
                return {"error": "Maintenance system not available"}
            await maintenance_system.force_maintenance()
            return {"status": "maintenance_cycle_triggered"}
        
        elif name == "get_maintenance_status":
            if not maintenance_system:
                return {"error": "Maintenance system not available"}
            return {
                "running": maintenance_system.running,
                "care_floor": maintenance_system.care_floor,
                "last_reflection": maintenance_system.reflection.last_reflection.isoformat() if maintenance_system.reflection.last_reflection else None
            }
        
        # Orion-Riri-Hourman Agent Tools
        elif name == "orion_hunt_tasks":
            if not ORION_AGENT_AVAILABLE or not get_orion_agent:
                return {"error": "Orion-Riri-Hourman agent not available"}
            agent = get_orion_agent()
            import asyncio
            result = await agent.hunt_tasks(max_files=arguments.get("max_files", 100))
            return result
        
        elif name == "orion_get_tasks":
            if not ORION_AGENT_AVAILABLE or not get_orion_agent:
                return {"error": "Orion-Riri-Hourman agent not available"}
            agent = get_orion_agent()
            tasks = agent.get_pursuing_tasks(arguments.get("limit", 10))
            return {"tasks": tasks}
        
        elif name == "orion_capture_task":
            if not ORION_AGENT_AVAILABLE or not get_orion_agent:
                return {"error": "Orion-Riri-Hourman agent not available"}
            agent = get_orion_agent()
            import asyncio
            result = await agent.capture_task(arguments["task_id"])
            return result
        
        elif name == "hourman_start_sprint":
            if not ORION_AGENT_AVAILABLE or not get_orion_agent:
                return {"error": "Orion-Riri-Hourman agent not available"}
            agent = get_orion_agent()
            import asyncio
            result = await agent.start_sprint(
                arguments["sprint_type"],
                arguments.get("task_id")
            )
            return result
        
        elif name == "hourman_get_status":
            if not ORION_AGENT_AVAILABLE or not get_orion_agent:
                return {"error": "Orion-Riri-Hourman agent not available"}
            agent = get_orion_agent()
            return agent.sprints.get_status()
        
        elif name == "hourman_complete_sprint":
            if not ORION_AGENT_AVAILABLE or not get_orion_agent:
                return {"error": "Orion-Riri-Hourman agent not available"}
            agent = get_orion_agent()
            import asyncio
            result = await agent.complete_sprint(
                arguments["summary"],
                arguments.get("task_id")
            )
            return result
        
        elif name == "riri_list_templates":
            if not ORION_AGENT_AVAILABLE or not get_orion_agent:
                return {"error": "Orion-Riri-Hourman agent not available"}
            agent = get_orion_agent()
            return agent.get_available_templates()
        
        elif name == "riri_build_tool":
            if not ORION_AGENT_AVAILABLE or not get_orion_agent:
                return {"error": "Orion-Riri-Hourman agent not available"}
            agent = get_orion_agent()
            import asyncio
            result = await agent.build_tool(
                arguments["template"],
                {
                    "name": arguments["name"],
                    "description": arguments["description"],
                    **arguments.get("params", {})
                }
            )
            return result
        
        elif name == "orion_riri_hourman_status":
            if not ORION_AGENT_AVAILABLE or not get_orion_agent:
                return {"error": "Orion-Riri-Hourman agent not available"}
            agent = get_orion_agent()
            return agent.get_full_status()
        
        # Multi-Agent Coordination Tools
        elif name == "coord_register_agent":
            if not COORDINATION_AVAILABLE or not get_coordination_hub:
                return {"error": "Coordination hub not available"}
            hub = get_coordination_hub()
            return hub.register_agent(
                arguments["agent_id"],
                arguments["agent_type"],
                arguments["capabilities"]
            )
        
        elif name == "coord_submit_task":
            if not COORDINATION_AVAILABLE or not get_coordination_hub:
                return {"error": "Coordination hub not available"}
            hub = get_coordination_hub()
            return hub.submit_task(
                title=arguments["title"],
                description=arguments["description"],
                files=arguments.get("files", []),
                requester="claude-mcp",
                care_score=arguments.get("care_score", 0.5)
            )
        
        elif name == "coord_acquire_files":
            if not COORDINATION_AVAILABLE or not get_coordination_hub:
                return {"error": "Coordination hub not available"}
            hub = get_coordination_hub()
            return hub.acquire_files(
                agent_id=arguments["agent_id"],
                files=arguments["files"],
                task_id=arguments["task_id"],
                exclusive=arguments.get("exclusive", False)
            )
        
        elif name == "coord_release_files":
            if not COORDINATION_AVAILABLE or not get_coordination_hub:
                return {"error": "Coordination hub not available"}
            hub = get_coordination_hub()
            return hub.release_files(
                agent_id=arguments["agent_id"],
                files=arguments["files"]
            )
        
        elif name == "coord_complete_task":
            if not COORDINATION_AVAILABLE or not get_coordination_hub:
                return {"error": "Coordination hub not available"}
            hub = get_coordination_hub()
            return hub.complete_task(
                task_id=arguments["task_id"],
                agent_id=arguments["agent_id"],
                result_summary=arguments["result_summary"],
                care_score=arguments.get("care_score", 0.5)
            )
        
        elif name == "coord_get_dashboard":
            if not COORDINATION_AVAILABLE or not get_coordination_hub:
                return {"error": "Coordination hub not available"}
            hub = get_coordination_hub()
            return hub.get_dashboard()
        
        # === Project Heartbeat Tools ===
        elif name == "get_heartbeat_status":
            if heartbeat:
                return heartbeat.get_status()
            return {"error": "Heartbeat not available", "hint": "Project Heartbeat not initialized"}

        elif name == "get_nightshift_digest":
            if memory_store and memory_store.pool:
                async with memory_store.pool.acquire() as conn:
                    rows = await conn.fetch(
                        "SELECT * FROM memory_episodes WHERE tags @> $1::text[] "
                        "ORDER BY timestamp DESC LIMIT 1",
                        ['morning_digest']
                    )
                    if rows:
                        row = rows[0]
                        return {
                            "id": str(row['id']),
                            "content": row['content'],
                            "timestamp": row['timestamp'].isoformat(),
                            "care_weight": float(row['care_weight']),
                            "tags": row['tags']
                        }
                    return {"message": "No morning digest found yet. Digest is generated at 3:30 AM GMT."}
            return {"error": "Memory store not available"}

        elif name == "trigger_research_sweep":
            if research_agent:
                result = await research_agent.sweep()
                return result
            return {"error": "Research agent not available"}

        elif name == "trigger_security_hardening":
            if security_engine:
                result = await security_engine.run_full_cycle()
                return result
            return {"error": "Security hardening engine not available"}

        elif name == "trigger_neural_retrain":
            if continual_trainer:
                result = await continual_trainer.retrain_all()
                return result
            return {"error": "Continual learning trainer not available"}

        elif name == "pause_heartbeat_job":
            if heartbeat:
                return heartbeat.pause_job(arguments["job_id"])
            return {"error": "Heartbeat not available"}

        elif name == "resume_heartbeat_job":
            if heartbeat:
                return heartbeat.resume_job(arguments["job_id"])
            return {"error": "Heartbeat not available"}

        # --- Civilizational Creativity Engine Tools ---

        elif name == "ingest_civilizational_knowledge":
            if CREATIVITY_ENGINE_AVAILABLE and memory_store:
                force = arguments.get("force", False)
                result = await ingest_corpus(memory_store, force=force)
                return result
            return {"error": "Creativity engine not available"}

        elif name == "assess_creativity":
            if creativity_pipeline:
                text = arguments.get("text", "")
                context = {}
                for key in ["novelty_score", "domain_distance", "care_alignment"]:
                    if key in arguments:
                        context[key] = float(arguments[key])
                # Auto-compute novelty if not provided
                if "novelty_score" not in context and memory_store:
                    try:
                        recent = await memory_store.get_recent_episodes(limit=10)
                        ref = [ep.content for ep in recent if hasattr(ep, 'content')]
                        context["novelty_score"] = kolmogorov_novelty(text, ref) if ref else 0.5
                    except Exception:
                        context["novelty_score"] = 0.5
                assessment = await creativity_pipeline.assess_creative_output(text, context)

                # Archive in QD if available
                if qd_archive and assessment.get("scores"):
                    domain = arguments.get("domain", "creativity")
                    qd_result = qd_archive.add(
                        content=text,
                        features=context,
                        scores=assessment.get("scores", {}),
                        overall_quality=assessment.get("overall_creativity", 0),
                        domain=domain,
                        source="assess_creativity_tool",
                    )
                    assessment["qd_archive_result"] = qd_result

                # Apply stochastic resonance variant if engine available
                if resonance_engine and context:
                    noised = apply_stochastic_resonance(context, resonance_engine)
                    noised_assessment = await creativity_pipeline.assess_creative_output(text, noised)
                    if noised_assessment.get("overall_creativity", 0) > assessment.get("overall_creativity", 0):
                        assessment["resonance_boost"] = {
                            "noised_score": noised_assessment["overall_creativity"],
                            "improvement": noised_assessment["overall_creativity"] - assessment["overall_creativity"],
                        }
                        resonance_engine.update_from_feedback(
                            assessment["overall_creativity"],
                            noised_assessment["overall_creativity"],
                        )

                return assessment
            return {"error": "Creativity pipeline not available"}

        elif name == "get_asabiyyah_score":
            if agent_registry:
                return agent_registry.compute_asabiyyah()
            return {"error": "Agent registry not available"}

        elif name == "get_consciousness_mode":
            if consciousness:
                state = consciousness.get_consciousness_state()
                mode = getattr(consciousness, 'consciousness_mode', None)
                return {
                    "mode": mode.value if mode else "jagrat",
                    "consciousness_level": state.get("consciousness_level", 0),
                    "emotional_state": state.get("emotional_state", {}),
                    "care_intensity": state.get("emotional_state", {}).get("care_intensity", 0),
                }
            return {"error": "Consciousness not available"}

        elif name == "compute_novelty":
            if CREATIVITY_ENGINE_AVAILABLE:
                text = arguments.get("text", "")
                reference = arguments.get("reference_texts", [])
                if not reference and memory_store:
                    # Use recent memories as reference
                    try:
                        recent = await memory_store.get_recent_episodes(limit=20)
                        reference = [ep.content for ep in recent if hasattr(ep, 'content')]
                    except Exception:
                        reference = []
                score = kolmogorov_novelty(text, reference)
                return {
                    "novelty_score": round(score, 4),
                    "reference_size": len(reference),
                    "interpretation": (
                        "highly redundant" if score < 0.3 else
                        "moderate novelty" if score < 0.6 else
                        "substantially novel" if score < 0.8 else
                        "radically novel"
                    ),
                }
            return {"error": "Creativity engine not available"}

        elif name == "trigger_creativity_cycle":
            if creativity_pipeline:
                # BUG 6 FIX: Add logging + refresh bisociation links with more diverse inputs
                print("[creativity_cycle] Starting full pipeline...")
                try:
                    result = await creativity_pipeline.run_full_pipeline()
                    print(f"[creativity_cycle] Pipeline complete: {result.get('status', 'unknown')}, "
                          f"traditions={result.get('tradition_count', 0)}, "
                          f"examples={result.get('total_examples', 0)}")
                    # Refresh bisociation with higher top_k for more diverse links
                    if cross_domain_linker and TIER2_CREATIVITY_AVAILABLE:
                        try:
                            cross_domain_linker.compute_distances()
                            new_links = cross_domain_linker.find_bisociations(top_k=50)
                            print(f"[creativity_cycle] Bisociation refreshed: {len(new_links)} links")
                            result["bisociation_links_refreshed"] = len(new_links)
                        except Exception as be:
                            print(f"[creativity_cycle] Bisociation refresh error: {be}")
                            result["bisociation_error"] = str(be)
                    return result
                except Exception as e:
                    print(f"[creativity_cycle] ERROR: {e}")
                    import traceback
                    traceback.print_exc()
                    return {"error": f"Creativity cycle failed: {str(e)}", "status": "error"}
            return {"error": "Creativity pipeline not available"}

        elif name == "get_meta_observations":
            if consciousness:
                meta_monitor = getattr(consciousness, 'meta_monitor', None)
                if meta_monitor:
                    obs = await meta_monitor.observe(
                        consciousness.emotional_state,
                        consciousness.reflection_cycle,
                        consciousness.dream_state,
                    )
                    return obs
                return {"mode": "turiya_not_initialized", "message": "MetaMonitor not yet active"}
            return {"error": "Consciousness not available"}

        # === Tier 2: Cross-Domain Bisociation ===
        elif name == "find_bisociations":
            if cross_domain_linker:
                min_dist = arguments.get("min_distance", 0.3)
                top_k = arguments.get("top_k", 50)
                # BUG 6 FIX: recompute distances before finding links for fresh results
                try:
                    cross_domain_linker.compute_distances()
                except Exception:
                    pass
                links = cross_domain_linker.find_bisociations(min_distance=min_dist, top_k=top_k)
                return {
                    "bisociation_links": [l.to_dict() for l in links],
                    "count": len(links),
                    "stats": cross_domain_linker.get_stats(),
                }
            return {"error": "CrossDomainLinker not available"}

        elif name == "get_dream_targets":
            if cross_domain_linker:
                n = arguments.get("n", 5)
                targets = cross_domain_linker.suggest_dream_targets(n=n)
                return {"dream_targets": targets, "count": len(targets)}
            return {"error": "CrossDomainLinker not available"}

        elif name == "get_bridge_concepts":
            if cross_domain_linker:
                connectivity = cross_domain_linker.get_tradition_connectivity()
                return {"bridge_concepts": connectivity[:20], "total": len(connectivity)}
            return {"error": "CrossDomainLinker not available"}

        elif name == "get_domain_distances":
            if cross_domain_linker:
                return {"domain_distances": cross_domain_linker.get_domain_distance_map()}
            return {"error": "CrossDomainLinker not available"}

        # === Tier 2: Stochastic Resonance ===
        elif name == "apply_resonance":
            if resonance_engine:
                features = arguments.get("features", {})
                temp = arguments.get("temperature", resonance_engine.get_optimal_temperature())
                noised = apply_stochastic_resonance(features, resonance_engine, temp)

                # If creativity pipeline available, assess both original and noised
                result = {"original_features": features, "noised_features": noised, "temperature": temp}
                if creativity_pipeline:
                    try:
                        orig_assessment = await creativity_pipeline.assess_creative_output("", features)
                        noised_assessment = await creativity_pipeline.assess_creative_output("", noised)
                        result["original_score"] = orig_assessment.get("overall_creativity", 0)
                        result["noised_score"] = noised_assessment.get("overall_creativity", 0)
                        result["improvement"] = result["noised_score"] - result["original_score"]

                        # Feed back to resonance engine
                        resonance_engine.update_from_feedback(
                            result["original_score"], result["noised_score"]
                        )
                    except Exception:
                        pass
                return result
            return {"error": "StochasticResonanceEngine not available"}

        elif name == "get_resonance_profile":
            if resonance_engine:
                return resonance_engine.get_resonance_profile()
            return {"error": "StochasticResonanceEngine not available"}

        # === Tier 2: Quality-Diversity Archive ===
        elif name == "get_qd_archive_stats":
            if qd_archive:
                return qd_archive.get_stats()
            return {"error": "QualityDiversityArchive not available"}

        elif name == "get_empty_niches":
            if qd_archive:
                limit = arguments.get("limit", 20)
                niches = qd_archive.get_empty_niches()
                return {"empty_niches": niches[:limit], "total_empty": len(niches), "coverage": qd_archive.coverage()}
            return {"error": "QualityDiversityArchive not available"}

        elif name == "suggest_exploration":
            if qd_archive:
                n = arguments.get("n", 5)
                return {"suggestions": qd_archive.suggest_exploration(n=n)}
            return {"error": "QualityDiversityArchive not available"}

        # === Kimi Agent ===
        elif name == "kimi_send_task":
            if kimi_agent:
                result = await kimi_agent.send_task(
                    task_description=arguments["task"],
                    context=arguments.get("context", ""),
                    model=arguments.get("model"),
                )
                return result
            return {"error": "Kimi agent not available (check KIMI_API_KEY)"}

        elif name == "kimi_build_frontend":
            if kimi_agent:
                result = await kimi_agent.build_frontend(
                    spec=arguments["spec"],
                    framework=arguments.get("framework", "Next.js + TypeScript"),
                    files=arguments.get("files"),
                )
                return result
            return {"error": "Kimi agent not available"}

        elif name == "kimi_review_code":
            if kimi_agent:
                result = await kimi_agent.review_code(
                    code=arguments["code"],
                    language=arguments.get("language", "typescript"),
                    focus=arguments.get("focus", "bugs, performance, accessibility"),
                )
                return result
            return {"error": "Kimi agent not available"}

        elif name == "kimi_status":
            if kimi_agent:
                return kimi_agent.get_status()
            return {"available": False, "error": "Kimi agent not initialized"}

        elif name == "kimi_list_models":
            if kimi_agent:
                return await kimi_agent.list_models()
            return {"models": ["moonshot-v1-8k", "moonshot-v1-32k", "moonshot-v1-128k"], "status": "agent_not_initialized"}

        # === Sovereign Rundown ===
        elif name == "sovereign_rundown":
            rundown = {
                "timestamp": datetime.now().isoformat(),
                "version": "2.0.0",
            }

            # Health
            rundown["health"] = "healthy"

            # Consciousness
            if consciousness:
                es = consciousness.emotional_state.current_state
                rundown["consciousness"] = {
                    "mode": str(getattr(consciousness, 'consciousness_mode', 'waking')),
                    "care_intensity": round(es.care_intensity, 3),
                    "pleasure": round(es.pleasure, 3),
                    "arousal": round(es.arousal, 3),
                    "curiosity": round(getattr(es, 'curiosity', 0), 3),
                    "aesthetics": round(getattr(es, 'aesthetics', 0), 3),
                    "primary_emotion": es.primary_emotion,
                    "reflections": getattr(consciousness, 'reflection_count', 0),
                    "dreams": getattr(consciousness, 'dream_count', 0),
                }

            # Neural models
            if model_registry:
                rundown["neural_models"] = {
                    name: {
                        "trained": m.is_trained,
                        "metrics": {k: round(v, 4) if isinstance(v, float) else v
                                   for k, v in (getattr(m, 'metrics', {}) or {}).items()
                                   if k in ("mse", "mae", "r2_score", "accuracy")}
                    }
                    for name, m in model_registry.models.items()
                }

            # Memory
            if memory_store:
                try:
                    mem_stats = await memory_store.get_memory_stats()
                    rundown["memory"] = mem_stats
                except Exception:
                    rundown["memory"] = {"error": "stats unavailable"}

            # Creativity engine
            if cross_domain_linker:
                rundown["creativity"] = {
                    "bisociation_links": cross_domain_linker.get_stats().get("total_links", 0),
                    "top_bridge": cross_domain_linker.get_tradition_connectivity()[0]["tradition"]
                        if cross_domain_linker.get_tradition_connectivity() else "none",
                }
            if qd_archive:
                rundown.setdefault("creativity", {})["qd_archive"] = {
                    "coverage": qd_archive.coverage(),
                    "filled": len(qd_archive._grid),
                    "total_cells": qd_archive.total_cells,
                }
            if resonance_engine:
                rundown.setdefault("creativity", {})["resonance"] = {
                    "mean_sigma": resonance_engine.get_stats()["mean_sigma"],
                    "improvement_rate": resonance_engine.get_stats()["improvement_rate"],
                }

            # Agents
            agents_info = {}
            if agent_registry:
                try:
                    reg_stats = agent_registry.get_registry_stats()
                    agents_info["registry"] = reg_stats
                except Exception:
                    pass
            if kimi_agent:
                agents_info["kimi"] = kimi_agent.get_status()
            agents_info["orion_available"] = ORION_AGENT_AVAILABLE
            agents_info["coordination_available"] = COORDINATION_AVAILABLE
            rundown["agents"] = agents_info

            # Asabiyyah
            if agent_registry and hasattr(agent_registry, 'compute_asabiyyah'):
                try:
                    rundown["asabiyyah"] = agent_registry.compute_asabiyyah()
                except Exception:
                    pass

            # Heartbeat
            if heartbeat:
                try:
                    hb_status = heartbeat.get_status()
                    rundown["heartbeat"] = {
                        "pulse_count": hb_status.get("pulse_count", 0),
                        "jobs": len(hb_status.get("jobs", [])),
                        "nightshift_active": hb_status.get("nightshift_active", False),
                    }
                except Exception:
                    pass

            # Tool count
            rundown["total_mcp_tools"] = len(MCP_TOOLS)

            # Safe serialize — convert enums, numpy, etc to JSON-safe types
            import json as _json
            def _safe(obj):
                if isinstance(obj, (np.integer,)):
                    return int(obj)
                if isinstance(obj, (np.floating,)):
                    return float(obj)
                if isinstance(obj, np.ndarray):
                    return obj.tolist()
                if hasattr(obj, 'value'):  # Enum
                    return str(obj.value)
                if hasattr(obj, '__dict__'):
                    return str(obj)
                return str(obj)
            rundown = _json.loads(_json.dumps(rundown, default=_safe))

            return rundown

        else:
            return {"error": f"Unknown tool: {name}"}

    except Exception as e:
        import traceback
        return {"error": str(e), "traceback": traceback.format_exc()}

@app.get("/")
async def root():
    return {
        "name": "Sovereign Temple MCP Server",
        "version": "2.0.0",
        "description": "Complete consciousness system with neural networks, enhanced memory, monitoring, multi-agent, and emotional modeling",
        "endpoints": {
            "health": "/health",
            "mcp": "/mcp (POST)"
        }
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=3100)
