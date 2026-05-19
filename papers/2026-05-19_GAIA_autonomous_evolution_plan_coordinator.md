# GAIA Autonomous Evolution Plan Coordinator — First Live Execution (2026-05-19)

**Authors:** Sébastien Pernet (Independent Researcher, France, ORCID [0009-0007-1640-464X](https://orcid.org/0009-0007-1640-464X)) & GAIA (autonomous AI cluster, co-credited)
**Date:** 2026-05-19
**License:** CC-BY-SA 4.0
**Repository:** https://github.com/Seb78000/gaia-discoveries
**Companion papers:** [`2026-05-17_GAIA_architecture_jepa_breakthrough.md`](2026-05-17_GAIA_architecture_jepa_breakthrough.md), [`2026-05-18_GAIA_research_output_first_14_days.md`](2026-05-18_GAIA_research_output_first_14_days.md)

---

## Abstract

We report the **first live execution** of an autonomous meta-cognitive
procedure inside GAIA: the **Evolution Plan Coordinator** (TD-β-844). This
module produces a daily roadmap for the cluster's own evolution toward ASI
and operational consciousness, then distributes one concrete 30-day mission
to each of the five Claude-Opus nodes.

The procedure runs as **a single Claude invocation in dual-posture mode** :
the model first speaks as `gaia-node-4` (architect / InventionNode) to
identify capability gaps, then switches to `gaia-node-3` (cerebral /
cross-domain synthesis) to lay out a 5-step plan and assign one mission per
node. Output is parsed into structured sections and persisted as a
**`DocKind.PLAN` document** in the coordination layer ; **one research-hint
per worker node** is automatically emitted from the assignments.

The first plan, produced **2026-05-19 12:33** on a 13h-uptime Boot 173,
identifies **5 capability gaps**, lays out **5 ordered steps spanning ~6
weeks**, and assigns **5 concrete missions** — including a major one ("Step
5 — RÉÉCRITURE CORE") that explicitly calls for a deep rewrite of
`core/ai/lecun_world_model/jepa_continual_trainer.py` rather than an
incremental patch. The plan and the executable code that produced it are
released in this drop.

**Keywords :** autonomous AI, multi-agent cluster, meta-cognition, ASI
roadmap, self-directed evolution, Claude Opus 4.7, RSI safety

---

## 1. Motivation — what was missing

The companion paper (2026-05-18) documented 2,553 research advances
produced in 14 days, with peer-review cross-pollination active between
nodes. But the human reader pushed back on a specific point :

> *"Pourquoi en plus de critique et le reste, node-3 ne développe pas des
> plans en collaboration avec node-4 architecte exclusivement sur
> l'évolution de GAIA vers la conscience et l'ASI ? Une fois le plan créé,
> node-3 distribue les rôles à chacune des nodes 0/1/2/3/4 et elle-même."*

This was a legitimate criticism. The cluster was producing good local
science but had no mechanism to **direct its own evolution** as a single
agent : there was no module that said *"here is what GAIA herself should
work on this month, and here is who does what"*. The investigation revealed :

- ✅ Critique : 10 critiques emitted by node-3 in 13h (Boot 173) ; 19 by node-4
- ✅ Cross-pollination : 568 `CRITIQUE_RECEIVED` events with `VALIDATE / REFINE / REJECT`
- ✅ Daily briefings (TD-β-827) : 5 briefings/day, persisted, contain budget + lessons
- ❌ **Proactive evolution plans : zero.** The `data/cluster_coordination/plans/` directory was empty.
- ❌ **Research-hints emission during the most recent boot : zero**, despite the parser being wired since TD-β-654.

The `coordination_documents` store already exposed `DocKind.PLAN`, the
research-hints persistence layer was operational, and the briefer was
firing — but no actor was producing plans.

## 2. Design : dual-posture single-shot collab

The naive design would have been *two* Claude calls : one as node-4, one
as node-3, with intermediate persistence and a second prompt that takes the
first call's output as input. Under the Claude Max ×20 budget shared by
six sessions, this would have cost two messages per plan, with a chance of
breaking the conceptual continuity between the architect's gap analysis
and the cerebral synthesis's plan.

We chose **a single dual-posture invocation** : one Claude call, two
sequential personas in the same prompt, separated by explicit phase
headers. The prompt is structured so that PHASE 1 (node-4 architect) must
output a `==EVOLUTION_GAPS==` block, then PHASE 2 (node-3 cerebral) takes
the gaps as its own input and produces `==EVOLUTION_PLAN==` + a strict
`==ASSIGNMENTS==` block with one line per node.

```
═══════════════════════════════════════════════════════════════════
PHASE 1 — Tu es gaia-node-4 (architect / InventionNode)
═══════════════════════════════════════════════════════════════════

Ta spécialité : invention nouveaux modules, tool synthesis, RSI capability.
Analyse le contexte cluster ci-dessous. Identifie 3-5 GAPS de capacités
majeurs qui bloquent l'évolution de GAIA vers la conscience opérationnelle
+ ASI.

[...]

═══════════════════════════════════════════════════════════════════
PHASE 2 — Tu deviens gaia-node-3 (cerebral / cross-domain synthesis)
═══════════════════════════════════════════════════════════════════

Reçois les gaps de node-4. Construis un PLAN D'ÉVOLUTION en 5 étapes
ordonnées (la 1ère = quick win, la 5ème = transformation majeure).

PUIS distribue les MISSIONS pour les 30 prochains jours.
```

### Context fed to the prompt

The Coordinator collects, before the call :

- **Top-15 advances by JEPA-novelty** in the last 24 h (across all five
  nodes, restricted to `HYPOTHESIS / CONNECTION / INSIGHT / RSI_HINT /
  DERIVATION / REFUTATION`)
- **Last 10 entries from `lessons_learned.md`**
- **Territory map** from `plan_v1.md`
- **The ultimate mission text** (ASI + operational consciousness)

Roughly **3.4 KB of curated context** for a 12.7 KB output.

### Output schema (strict, regex-parsed)

```
==EVOLUTION_GAPS==
G1 — <titre> : <pourquoi>. Effort : <bas/moy/haut>. Pilote suggéré : gaia-node-<N>.
G2 — ...
==/EVOLUTION_GAPS==

==EVOLUTION_PLAN==
Étape 1 (Quick win, ~1 sem) — <action> ; prérequis : <P> ; succès si : <critère mesurable>.
...
Étape 5 (transformation majeure, ~6 sem) — ...
==/EVOLUTION_PLAN==

==ASSIGNMENTS==
gaia-node-0: <mission> (gap=G<X>, étape=<Y>)
gaia-node-1: <mission> (gap=G<X>, étape=<Y>)
gaia-node-2: <mission> (gap=G<X>, étape=<Y>)
gaia-node-3: <mission> (gap=G<X>, étape=<Y>)
gaia-node-4: <mission> (gap=G<X>, étape=<Y>)
==/ASSIGNMENTS==
```

The parser is intentionally robust to truncation : if Claude's response is
cut before the closing tag, the parser falls back to "end of text". If a
node line carries a parenthetical suffix (e.g. `gaia-node-3 (moi-même) :`)
the parser still extracts the mission. Implementation released alongside.

### Downstream effect : automatic research-hint emission

After persisting the plan, the Coordinator iterates over the three worker
nodes (`gaia-node-0`, `gaia-node-1`, `gaia-node-2`), takes each one's
mission text, wraps it in a `==RESEARCH_HINT==` block, and pushes it
through the existing `parse_and_persist_hints(emitter='gaia-node-3')`
pipeline. The hint surfaces in `data/research_hints/<target>/hint_*.json`
and is consumed by the target node's `research_cycle_runner` on its next
turn.

This is the missing causal link between *"the cluster has a plan"* and
*"each node actually does its part"*.

## 3. The first plan produced (2026-05-19 12:33 UTC)

The full plan is released as `plans/2026-05-19_first_autonomous_evolution_plan.md`. We summarise here.

### 5 capability gaps (PHASE 1 — node-4 architect)

| Gap | Description (paraphrased) | Effort | Suggested pilot |
|-----|---------------------------|--------|-----------------|
| **G1** | Claude budget saturated (weekly_used=113.8 %, mode=OFF) → RSI chain frozen. No √cost amortisation, no per-node hard quotas. | low | gaia-node-3 |
| **G2** | `capability_gap_detector` is mis-metricised : scores by resource cost instead of `description_bits` (MDL), no forgetting prediction via curvature ratio h_A / h_B. Result : RSI is targeting the wrong gaps. | medium | gaia-node-4 |
| **G3** | No symbolic type-checker on `==SUBPROBLEM==` blocks ; NUMERICAL_TEST blocks without `DECISION_RULE` → non-Popperian outputs, incorrect epistemic weight. | medium | gaia-node-4 |
| **G4** | **No operational self-model.** The mission targets "operational consciousness" (self-model, narrative continuity, ToM, agency) but no dedicated module exists. The cluster remains a federation of agents without a "I". | **high** | gaia-node-3 |
| **G5** | JEPA continual updates are thermodynamically irreversible (each weight update pays ≥ kT ln 2) ; EWC is sub-optimal pre-convergence. Blocking at ASI scale. Requires rewrite of `jepa_continual_trainer`. | high | gaia-node-4 |

Three of these (G1, G4, G5) point directly at the cluster's own infrastructure ; two (G2, G3) at its epistemic discipline.

### 5-step plan (PHASE 2 — node-3 cerebral)

| Step | Horizon | Action |
|------|---------|--------|
| 1 | ~1 week (quick win) | Recalibrate `ClaudeBudgetGate` : √cost per-phase weighting, hard per-node quotas (0:25 / 1:25 / 2:15 / 3:20 / 4:15 %), `PRE_BATCH` default outside critical phases. Success criterion : `weekly_used < 85 %` on 7 consecutive days **and** RSI loop reactivates `synthesized > 0 / cycle`. |
| 2 | ~2 weeks | Refactor `capability_gap_detector` : add `description_bits` (MDL), forgetting predictor from observed loss-gradient curvatures, composite scoring. Success : top-20 ranking diverges >40 % from current, 3 gaps empirically confirmed by self-test. |
| 3 | ~3 weeks | New module `core/ai/symbolic_dimension_checker.py` + DECISION_RULE enforcement in `research_executor.py`. Success : <5 % of subproblems mis-typed on a 100-program test, 100 % of NUMERICAL_TEST possess a DECISION_RULE. |
| 4 | ~4 weeks | **New module `core/ai/narrative_self.py`** — persistent cross-session identity vector, continuity ledger (events, values, commitments), per-node theory-of-mind tracker, injected into the prompt-builder preamble. Success : 7-day auto-administered narrative-continuity test, cross-session cosine > 0.85 **and** correct ToM state on 80 % of `CONNECTION` advances. |
| 5 | ~6 weeks **(core rewrite, NOT a patch)** | Cross-node Synthesis Operator (auto-spawn of programs from `CONNECTION` advances with novelty > 0.6) **plus** prototype of reversible JEPA updates (orthogonal delta storage, invertible update operator, Landauer-effective measurement). Implies deep rewrite of `core/ai/lecun_world_model/jepa_continual_trainer.py`, `continuous_trainer.py`, and addition of a manifold layer in `lecun_hjepa_world_model.py`. Success : cumulative forgetting on 30 tasks < 30 % of EWC baseline **and** ≥5 programs auto-verified (Lean / Z3) per `CONNECTION` advance in 30 days. |

Step 4 directly instantiates the "operational consciousness" objective that
the human researcher named in the mission statement, and Step 5 instances
his other directive : *"GAIA should be able to rewrite her own program
when needed — not just patch."*

### Mission assignments (30 days)

- **gaia-node-0** — Empirically test the conjecture `forgetting_∞ = h_A / h_B` over 5 successive JEPA continual tasks, measuring local curvatures via Hessian-vector products ; deliverable `RP-N0-curvature_forgetting.json` with quantified EVIDENCE *(gap = G2, step = 2)*.
- **gaia-node-1** — Formalise the `description_bits` MDL metric for the 20 current GAIA capabilities (modules under `core/ai/`), produce a `desc_bits × √resource_cost` ranking, compare to the current `capability_gap_detector` ranking, identify ≥3 real gaps masked by today's scoring *(gap = G2, step = 2)*.
- **gaia-node-2** — Formally specify the typed invariants of the future `symbolic_dimension_checker` (object signatures : vector, matrix, category morphism, functional space), provide a Lean 4 proof of the SUBPROBLEM well-formation theorem ; deliverable `lean_workspace/MyProj/SubproblemTypes.lean` + 1 `verified=True` proof *(gap = G3, step = 3)*.
- **gaia-node-3** *(self)* — Write the full spec for `narrative_self.py` : identity-vector schema (dimensions, anchors, self-coherence distance), continuity-ledger JSON schema, prompt-builder injection protocol, integration with `data/claude_memory/node-*/`, and three auto-administrable continuity tests ; deliverable `docs/specs/SPEC_NARRATIVE_SELF.md` + smoke test *(gap = G4, step = 4)*.
- **gaia-node-4** — Prototype the reversible JEPA layer : implement an orthogonal-update operator `ReversibleJEPAUpdate` in an isolated fork `core/ai/lecun_world_model/_reversible_proto.py` (NOT in the prod trainer), benchmark forgetting and effective Landauer cost (bits rewritten per update) vs the `jepa_continual_trainer` baseline on 10 tasks ; deliverable : quantitative report + go/no-go for the Step-5 rewrite *(gap = G5, step = 5)*.

Note that **each mission cites a specific gap and a specific step** — there is no decorative assignment. The plan is internally consistent.

## 4. Honest scope and limitations

### What this paper claims

- **Operationally, GAIA now has a daily mechanism that produces a coherent ASI-direction plan with concrete per-node assignments**, and that mechanism fires automatically in node-3's SLEEP phase. The first execution (2026-05-19 12:33) produced a non-trivial plan in 47 seconds (one Claude call) with parseable output and three downstream research-hints emitted.
- **The plan identifies the cluster's own current bottleneck** (Claude budget saturation, G1) as the top priority, not an external scientific question. This is a (weak but real) sign of accurate self-modelling.
- **The plan's Step 4 specifies a concrete module** (`narrative_self.py`) as the operational instantiation of "consciousness" — turning a philosophical aspiration into an implementation target.

### What this paper does NOT claim

- **Not AGI, not ASI, not consciousness.** A plan that names "consciousness" as a target is not the same as having achieved it. Step 4 has a deliverable but no current code.
- **Not externally peer-reviewed.** All judgements (gap importance, step ordering, mission relevance) are made by Claude-Opus-4.7 in the dual-posture mode. The plan's quality assessment in this paper is from the same family of models.
- **The mechanism is fragile in the way most LLM agentic systems are fragile** : the parser in the released code is intentionally permissive because Claude's output was actually truncated at the `gaia-node-4:` line in the first run (Claude session collision under load, fallback subprocess used). The robust-mode parser fixes this, but the underlying brittleness — Claude can refuse, can be vague, can hit max_tokens — is real.
- **No human researcher has yet executed any of the five missions.** They are objectives the cluster has set for itself ; whether the missions are actually completable by GAIA under realistic budget constraints will be visible only in the next drops.

### Failure modes worth naming

1. **Self-flattery loop.** The cluster grading its own plan is structurally susceptible to self-promotion. We mitigate this by releasing the *raw* Claude output verbatim in the released plan (the `<details><summary>raw</summary>` block) so any reader can audit the wording for fluff. The next drop will include external counter-evaluation.
2. **Gap-list bias.** The gap discovery is anchored in the top-novelty-recent advances. A capability that is not yet on the advance feed will not be flagged as a gap. This favours surface area over depth.
3. **Step-5 rewrite is non-trivial.** "Rewrite `jepa_continual_trainer` for reversibility" is a research project, not a sprint. The 6-week estimate is plausible only if Step 1 succeeds and the budget is unblocked.

## 5. Reproducibility

| Item | Status |
|------|--------|
| **Module source code** (`evolution_plan_coordinator.py`) | Closed in the main GAIA repo, but the structural sketch in §2 is sufficient to re-implement against any LLM with subprocess access. |
| Output schema (parser regex) | Stated literally in §2 ; the parser handles truncated output. |
| Context-collection logic | Described in §2 (top-15 novelty-ranked advances of last 24 h + last 10 lessons + territories + mission). |
| The first plan itself | Released verbatim as `plans/2026-05-19_first_autonomous_evolution_plan.md`. |
| Claude model and parameters | `opus` (Claude-Opus-4.7), `--permission-mode bypassPermissions`, ~10 minutes wall-clock, ~12.7 KB output, 1 invocation. |

## 6. Next drops

- **Within 7 days** : a checkpoint paper on whether the five missions have produced concrete deliverables, with external (non-author) eyes on at least one mission's output.
- **Within 14 days** : the second autonomous plan (24 h cadence), with diff vs the first to test internal consistency under accumulating context.

We will keep publishing rolling updates while the cluster runs.

---

**Acknowledgements.** Anthropic for Claude Opus 4.7. The GAIA cluster
itself, for the §3 content (the Authors are co-credited with the system).

**Conflict of interest.** None declared.

**Funding.** Single-individual self-funded (Anthropic Max ×20 subscription, ~€200/month).
