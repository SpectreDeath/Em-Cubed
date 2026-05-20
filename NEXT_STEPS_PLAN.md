# Em-Cubed: Next Steps Plan
## Based on Development Ideas Analysis

**Plan Created:** 2026-05-16  
**Current Branch:** `master`  
**Version Target:** v0.6.0  
**Total Estimated Effort:** 20-40 hours across 3 phases

---

## EXECUTIVE SUMMARY

Based on analysis of the development ideas file and current project state, this plan prioritizes the most valuable enhancements that will:
1. Improve production readiness and security
2. Enhance developer experience and ecosystem growth
3. Expand capabilities for complex workflows
4. Establish foundations for future scaling

The plan focuses on 5 high-impact initiatives selected from the 15 ideas, balancing immediate value with strategic positioning.

---

## PRIORITY INITIATIVES

### 🥇 Phase 1: Production Hardening (8-12 hours)
*Goal: Make Em-Cubed production-safe for untrusted skill execution*

#### 1. Containerized Skill Execution (Highest Impact)
**Why:** Critical for security when executing skills from external/untrusted sources
**Components:**
- Docker/Podman isolation for skill execution
- Resource limits (CPU, memory, time)
- Filesystem restrictions
- Network access controls
**Files to modify:**
- `src/em_cubed/plugin_manager.py` (add container execution mode)
- `src/em_cubed/surfaces/base.py` (add container interface)
- `docs/SECURITY.md` (new document)
**Estimated:** 4-6 hours

#### 2. Cost & Rate Limiting Management (High Impact)
**Why:** Prevents runaway LLM API costs in production workflows
**Components:**
- Token usage tracking per skill/execution
- Configurable budget limits
- Rate limiting middleware for LLM skills
- Cost estimation before execution
**Files to modify:**
- `src/em_cubed/skills/telemetry.py` (add cost tracking)
- `src/em_cubed/skills/executor.py` (add rate limiting)
- `docs/COST_MANAGEMENT.md` (new document)
**Estimated:** 3-4 hours

#### 3. Dynamic Skill Discovery & Registry Federation (Strategic)
**Why:** Enables skill sharing and ecosystem growth beyond local installation
**Components:**
- Remote skill registry API (GitHub, internal hubs)
- Authentication/authorization for private registries
- Skill caching and version management
- Trust verification for external skills
**Files to modify:**
- `src/em_cubed/skills/registry.py` (add remote discovery)
- `src/em_cubed/skills/recommender.py` (integrate remote skills)
- `docs/SKILL_REGISTRY.md` (new document)
**Estimated:** 4-6 hours

---

### 🥈 Phase 2: Developer Experience & Ecosystem (10-15 hours)
*Goal: Accelerate skill development and improve usability*

#### 4. Language Server Protocol (LSP) for SKILL.md (High Impact)
**Why:** Significantly improves developer experience with real-time feedback
**Components:**
- VS Code extension providing:
  - SKILL.md syntax highlighting
  - Frontmatter validation
  - Input/output schema autocomplete
  - Surface availability checking
  - Skill dependency validation
**Files to create:**
- `lsp/skill_lsp/` (new directory for LSP server)
- `lsp/vscode-extension/` (VS Code extension)
- `docs/LSP_GUIDE.md` (new document)
**Estimated:** 6-8 hours

#### 5. Semantic Skill Search Engine (Strategic)
**Why:** Transforms skill discovery from keyword matching to intent understanding
**Components:**
- Local vector embeddings (SentenceTransformers)
- Semantic similarity search
- Skill capability embedding generation
- Hybrid search (keyword + semantic)
**Files to modify:**
- `src/em_cubed/skills/recommender.py` (add semantic search)
- `src/em_cubed/skills/telemetry.py` (add embedding generation)
- `docs/SEMANTIC_SEARCH.md` (new document)
**Estimated:** 4-7 hours

---

### 🥉 Phase 3: Advanced Capabilities (12-18 hours)
*Goal: Enable sophisticated multi-surface workflows and observability*

#### 6. Cross-Surface Data Type Standardization (High Impact)
**Why:** Eliminates friction in multi-surface workflows by auto-handling type conversions
**Components:**
- Unified type system across Python/Prolog/Hy/Z3/Datalog
- Automatic serialization/deserialization at surface boundaries
- Type validation and coercion framework
- Developer annotations for explicit type control
**Files to modify:**
- `src/em_cubed/context.py` (new type standardization layer)
- `src/em_cubed/skills/executor.py` (integrate type handling)
- Surface implementations (add type adapters)
- `docs/TYPE_SYSTEM.md` (new document)
**Estimated:** 6-9 hours

#### 7. Real-time Observability Dashboard (Strategic)
**Why:** Provides visibility into workflow execution for debugging and monitoring
**Components:**
- Lightweight web dashboard (FastAPI + React/Lit)
- Real-time DAG execution visualization
- Performance metrics and bottlenecks
- Skill usage statistics and trends
- Trace context visualization
**Files to create:**
- `dashboard/` (new directory for web interface)
- `src/em_cubed/telemetry/api.py` (new API endpoints)
- `docs/OBSERVABILITY.md` (new document)
**Estimated:** 6-9 hours

---

## SECONDARY CONSIDERATIONS

### Valuable but Lower Priority (for future phases):
- **WASM Surface:** Excellent for language diversity but complex implementation
- **Rust Execution Surface:** High performance gain but niche use case
- **Streaming LLM Outputs:** Improves UX but requires significant LLM surface changes
- **Distributed DAG Execution:** Important for scaling but premature before local optimization
- **Durable Execution:** Valuable for reliability but adds complexity
- **Event-Driven Workflows:** Expands use cases but requires message broker integration
- **Visual Workflow Designer:** Great for accessibility but lower technical priority
- **Automated Skill Generation:** Innovative but depends on LSP and semantic search foundations

---

## IMPLEMENTATION APPROACH

### Risk Mitigation:
1. **Incremental Delivery:** Each initiative delivers standalone value
2. **Backward Compatibility:** All changes maintain existing APIs
3. **Feature Flags:** Major changes opt-in via configuration
4. **Comprehensive Testing:** Unit and integration tests for all new features
5. **Documentation First:** Docs created alongside implementation

### Success Metrics:
- All new features have >80% test coverage
- Zero breaking changes to public APIs
- Documentation completeness score >90%
- Performance impact <5% for existing workflows
- Security audit passes for container execution

### Dependencies:
- Phase 1 can start immediately (based on current stable code)
- Phase 2 benefits from Phase 1 telemetry enhancements
- Phase 3 builds on Phase 2 developer tools

---

## NEXT ACTIONS

### Immediate (Week 1):
1. Review and approve this plan
2. Set up feature branches for Phase 1 initiatives
3. Begin containerized execution spike (proof of concept)

### Short-term (Weeks 2-3):
1. Complete Phase 1 initiatives
2. Begin Phase 2 LSP development
3. Update project documentation with new features

### Medium-term (Weeks 4-6):
1. Complete Phase 2 initiatives
2. Begin Phase 3 type standardization work
3. Conduct internal dogfooding of new features

### Long-term (Ongoing):
1. Monitor adoption and feedback
2. Plan Phase 4 based on usage patterns
3. Continue ecosystem development

---

## CONCLUSION

This plan focuses on the most valuable development ideas that will transform Em-Cubed from a promising framework into a production-ready, ecosystem-capable platform. By prioritizing security, developer experience, and extensibility, we lay the groundwork for sustainable growth while delivering immediate value to users.

The selected initiatives address the highest-leverage points identified in the development ideas file, ensuring our efforts yield maximum impact for the investment.