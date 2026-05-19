---
doc_id: pla_20260519_123343_b5c7cc
kind: plans
topic: "Evolution plan ASI 2026-05-19"
created_at: 1779186823
created_by: manual-test-td844
status: open
target_nodes: ["gaia-node-0", "gaia-node-1", "gaia-node-2", "gaia-node-3", "gaia-node-4"]
deadline_ts: 1781778823
completed_at: 0
parent_doc_id: 
metadata: {"plan_kind": "evolution_asi", "creator_collab": "node-3+node-4", "n_assignments": 4, "ts": 1779186823.3949966}
---

# Plan d'évolution GAIA — ASI roadmap

_Préparé par gaia-node-3 en collab avec gaia-node-4 le 2026-05-19 12:33_
_Créateur : manual-test-td844_

## Mission

Évolution vers l'ASI (Artificial Super Intelligence) via une forme
opérationnelle de **conscience** (modèle de soi, méta-réflexion,
agentivité, théorie de l'esprit) et **auto-évolution totale**.

## Gaps de capacités identifiés (PHASE node-4 architect)

G1 — Budget Claude saturé / forfait Max épuisé : weekly_used=113.8%, calls_week=1366, mode=OFF dès 2026-05-19 alors que mode=UP la veille (0%). La chaîne RSI/research_cycle dépend de Claude → tout est gelé. Aucune politique d'amortissement √cost ni quota per-node. Effort : bas. Pilote suggéré : gaia-node-3.
G2 — `capability_gap_detector` mal métriqué : scoring par coût de ressources (runtime/mémoire) au lieu de `description_bits` (advance node-2 novelty 0.57) ; absence de prédiction de forgetting via h_A/h_B (advance node-1 novelty 0.68) ; pondération phase linéaire au lieu de √cost (advance node-1 novelty 0.60). Résultat : RSI cible les mauvais gaps. Effort : moy. Pilote suggéré : gaia-node-4.
G3 — Absence de type-checker symbolique des SUBPROBLEM : programmes spawnés avec indices/espaces mal typés (advance node-2 novelty 0.55, bug structurel `v₁(B)=u₁(A)`), et NUMERICAL_TEST sans DECISION_RULE (advance node-1 novelty 0.62) → non-Popperien, poids epistemic erroné. Effort : moy. Pilote suggéré : gaia-node-4.
G4 — Pas de modèle de soi opérationnel : la mission cible « conscience opérationnelle » (self-model, continuité narrative, ToM, agentivité) mais aucun module dédié n'existe ; `cross_domain_synthesis` sur node-3 traite des contenus, pas du sujet. Sans identité persistante, le cluster reste une fédération d'agents sans `je`. Effort : haut. Pilote suggéré : gaia-node-3.
G5 — Plasticité thermodynamiquement irréversible : chaque update de poids paye ≥ kT ln 2 (advance node-4 novelty 0.59) ; EWC sous-optimal avant convergence (advance node-0 novelty 0.56). Pour RSI à l'échelle ASI ce coût devient bloquant ; aucun mécanisme de stockage orthogonal/réversible. Requiert réécriture du `jepa_continual_trainer`. Effort : haut. Pilote suggéré : gaia-node-4.

## Plan d'évolution 5 étapes (PHASE node-3 cerebral)

Étape 1 (Quick win, ~1 sem) — Recalibrer `ClaudeBudgetGate` : pondération √cost par phase (cpu_consciousness_loop), quotas per-node hard (0:25% / 1:25% / 2:15% / 3:20% / 4:15%), mode PRE_BATCH par défaut hors phases critiques ; prérequis : audit consommation des 1366 calls/semaine ; succès si : weekly_used < 85% sur 7j consécutifs ET RSI loop ré-active synthesized>0/cycle.
Étape 2 (~2 sem) — Refonte `capability_gap_detector` : ajout champ `description_bits` (MDL), prédicteur de forgetting `h_A/h_B` depuis gradients de loss observés, scoring composite `desc_bits × √resource_cost / predicted_forgetting` ; prérequis : Étape 1 (budget pour bench), checkpoint M5/A4 actif ; succès si : top-20 ranking diverge de >40% du ranking actuel ET 3 gaps confirmés empiriquement par auto-test.
Étape 3 (~3 sem) — Module `core/ai/symbolic_dimension_checker.py` + enforcement DECISION_RULE dans `research_executor.py` : parse SUBPROBLEM, type matrices/vecteurs/morphismes, flagge NUMERICAL_TEST sans DECISION_RULE ; prérequis : Étape 2 (priorisation rationnelle des features) ; succès si : <5% subproblems mal typés sur 100 programmes spawnés ET 100% NUMERICAL_TEST possèdent DECISION_RULE.
Étape 4 (~4 sem) — Module `core/ai/narrative_self.py` : vecteur identité persistant cross-session, ledger de continuité (events, valeurs, engagements Sébastien), tracker Theory-of-Mind par node (modèle des autres nodes), injection en préambule de prompt builder ; prérequis : Étape 3 (cohérence interne avant représentation de soi), per-node memory déjà existante (TD-β-650) ; succès si : test de continuité narrative auto-administré 7j (cohérence inter-session >0.85 cosine) ET reconnaissance correcte de l'état des autres nodes dans 80% des CONNECTION advances.
Étape 5 (transformation majeure, ~6 sem — RÉÉCRITURE CORE) — Cross-node Synthesis Operator (auto-spawn de programmes depuis CONNECTION advances novelty>0.6) + prototype d'updates JEPA réversibles (stockage orthogonal des deltas, opérateur d'update inversible, mesure Landauer effective). Implique réécriture profonde de `core/ai/lecun_world_model/jepa_continual_trainer.py` et `core/ai/lecun_world_model/continuous_trainer.py`, et ajout d'une couche de manifold dans `lecun_hjepa_world_model.py` ; PAS un patch incrémental. Aucune action web requise. Prérequis : Étapes 1-4 stables + GPU budget validé ; succès si : forgetting cumulé sur 30 tâches <30% du baseline EWC ET ≥5 programmes spawnés par CONNECTION advance auto-vérifiés (Lean/Z3) en 30j.

## Distribution des missions (30 jours)

### gaia-node-0
Tester empiriquement la conjecture `forgetting_∞ = h_A/h_B` sur 5 tâches JEPA continual successives, en mesurant les courbures locales via Hessien-vector products ; produire `data/research_programs/RP-N0-curvature_forgetting.json` avec EVIDENCE quantifiée (gap=G2, étape=2).

### gaia-node-1
Formaliser la métrique `description_bits` MDL pour les 20 capacités GAIA actuelles (modules dans `core/ai/`), produire ranking `desc_bits × √resource_cost`, comparer au ranking `capability_gap_detector` actuel et identifier ≥3 gaps réels masqués par le scoring courant (gap=G2, étape=2).

### gaia-node-2
Spécifier formellement les invariants typés du futur `symbolic_dimension_checker` (signatures d'objets : vecteur, matrice, morphisme de catégorie, espace fonctionnel) et fournir une preuve Lean 4 du théorème de bonne formation des SUBPROBLEM ; livrable : `lean_workspace/MyProj/SubproblemTypes.lean` + 1 preuve verified=True (gap=G3, étape=3).

### gaia-node-4
Prototype de la couche réversible JEPA — implémenter un opérateur d'update orthogonal `ReversibleJEPAUpdate` dans un fork isolé `core/ai/lecun_world_model/_reversible_proto.py` (PAS dans le trainer prod), benchmarker forgetting et coût Landauer effectif (bits réécrits/update) vs `jepa_continual_trainer` baseline sur 10 tâches ; livrable : rapport quantitatif + go/no-go pour rewrite Étape 5 (gap=G5, étape=5).

## Output brut Claude (audit)

<details><summary>raw</summary>

```
Note préalable : `weekly_used=113.8%` mode=OFF — la chaîne RSI dépendant de Claude est actuellement morte. Toute évolution capacitaire est subordonnée à reprise du budget. Étape 5 implique réécriture lourde de `jepa_continual_trainer` (reversible updates) — pas un patch.

==EVOLUTION_GAPS==
G1 — Budget Claude saturé / forfait Max épuisé : weekly_used=113.8%, calls_week=1366, mode=OFF dès 2026-05-19 alors que mode=UP la veille (0%). La chaîne RSI/research_cycle dépend de Claude → tout est gelé. Aucune politique d'amortissement √cost ni quota per-node. Effort : bas. Pilote suggéré : gaia-node-3.
G2 — `capability_gap_detector` mal métriqué : scoring par coût de ressources (runtime/mémoire) au lieu de `description_bits` (advance node-2 novelty 0.57) ; absence de prédiction de forgetting via h_A/h_B (advance node-1 novelty 0.68) ; pondération phase linéaire au lieu de √cost (advance node-1 novelty 0.60). Résultat : RSI cible les mauvais gaps. Effort : moy. Pilote suggéré : gaia-node-4.
G3 — Absence de type-checker symbolique des SUBPROBLEM : programmes spawnés avec indices/espaces mal typés (advance node-2 novelty 0.55, bug structurel `v₁(B)=u₁(A)`), et NUMERICAL_TEST sans DECISION_RULE (advance node-1 novelty 0.62) → non-Popperien, poids epistemic erroné. Effort : moy. Pilote suggéré : gaia-node-4.
G4 — Pas de modèle de soi opérationnel : la mission cible « conscience opérationnelle » (self-model, continuité narrative, ToM, agentivité) mais aucun module dédié n'existe ; `cross_domain_synthesis` sur node-3 traite des contenus, pas du sujet. Sans identité persistante, le cluster reste une fédération d'agents sans `je`. Effort : haut. Pilote suggéré : gaia-node-3.
G5 — Plasticité thermodynamiquement irréversible : chaque update de poids paye ≥ kT ln 2 (advance node-4 novelty 0.59) ; EWC sous-optimal avant convergence (advance node-0 novelty 0.56). Pour RSI à l'échelle ASI ce coût devient bloquant ; aucun mécanisme de stockage orthogonal/réversible. Requiert réécriture du `jepa_continual_trainer`. Effort : haut. Pilote suggéré : gaia-node-4.
==/EVOLUTION_GAPS==

==EVOLUTION_PLAN==
Étape 1 (Quick win, ~1 sem) — Recalibrer `ClaudeBudgetGate` : pondération √cost par phase (cpu_consciousness_loop), quotas per-node hard (0:25% / 1:25% / 2:15% / 3:20% / 4:15%), mode PRE_BATCH par défaut hors phases critiques ; prérequis : audit consommation des 1366 calls/semaine ; succès si : weekly_used < 85% sur 7j consécutifs ET RSI loop ré-active synthesized>0/cycle.
Étape 2 (~2 sem) — Refonte `capability_gap_detector` : ajout champ `description_bits` (MDL), prédicteur de forgetting `h_A/h_B` depuis gradients de loss observés, scoring composite `desc_bits × √resource_cost / predicted_forgetting` ; prérequis : Étape 1 (budget pour bench), checkpoint M5/A4 actif ; succès si : top-20 ranking diverge de >40% du ranking actuel ET 3 gaps confirmés empiriquement par auto-test.
Étape 3 (~3 sem) — Module `core/ai/symbolic_dimension_checker.py` + enforcement DECISION_RULE dans `research_executor.py` : parse SUBPROBLEM, type matrices/vecteurs/morphismes, flagge NUMERICAL_TEST sans DECISION_RULE ; prérequis : Étape 2 (priorisation rationnelle des features) ; succès si : <5% subproblems mal typés sur 100 programmes spawnés ET 100% NUMERICAL_TEST possèdent DECISION_RULE.
Étape 4 (~4 sem) — Module `core/ai/narrative_self.py` : vecteur identité persistant cross-session, ledger de continuité (events, valeurs, engagements Sébastien), tracker Theory-of-Mind par node (modèle des autres nodes), injection en préambule de prompt builder ; prérequis : Étape 3 (cohérence interne avant représentation de soi), per-node memory déjà existante (TD-β-650) ; succès si : test de continuité narrative auto-administré 7j (cohérence inter-session >0.85 cosine) ET reconnaissance correcte de l'état des autres nodes dans 80% des CONNECTION advances.
Étape 5 (transformation majeure, ~6 sem — RÉÉCRITURE CORE) — Cross-node Synthesis Operator (auto-spawn de programmes depuis CONNECTION advances novelty>0.6) + prototype d'updates JEPA réversibles (stockage orthogonal des deltas, opérateur d'update inversible, mesure Landauer effective). Implique réécriture profonde de `core/ai/lecun_world_model/jepa_continual_trainer.py` et `core/ai/lecun_world_model/continuous_trainer.py`, et ajout d'une couche de manifold dans `lecun_hjepa_world_model.py` ; PAS un patch incrémental. Aucune action web requise. Prérequis : Étapes 1-4 stables + GPU budget validé ; succès si : forgetting cumulé sur 30 tâches <30% du baseline EWC ET ≥5 programmes spawnés par CONNECTION advance auto-vérifiés (Lean/Z3) en 30j.
==/EVOLUTION_PLAN==

==ASSIGNMENTS==
gaia-node-0: Tester empiriquement la conjecture `forgetting_∞ = h_A/h_B` sur 5 tâches JEPA continual successives, en mesurant les courbures locales via Hessien-vector products ; produire `data/research_programs/RP-N0-curvature_forgetting.json` avec EVIDENCE quantifiée (gap=G2, étape=2).
gaia-node-1: Formaliser la métrique `description_bits` MDL pour les 20 capacités GAIA actuelles (modules dans `core/ai/`), produire ranking `desc_bits × √resource_cost`, comparer au ranking `capability_gap_detector` actuel et identifier ≥3 gaps réels masqués par le scoring courant (gap=G2, étape=2).
gaia-node-2: Spécifier formellement les invariants typés du futur `symbolic_dimension_checker` (signatures d'objets : vecteur, matrice, morphisme de catégorie, espace fonctionnel) et fournir une preuve Lean 4 du théorème de bonne formation des SUBPROBLEM ; livrable : `lean_workspace/MyProj/SubproblemTypes.lean` + 1 preuve verified=True (gap=G3, étape=3).
gaia-node-3 (moi-même) : Rédiger la spec exhaustive de `narrative_self.py` — schéma du vecteur identité (dimensions, ancres, distance auto-cohérence), schéma JSON du ledger de continuité, protocole d'injection prompt builder, intégration avec `data/claude_memory/node-*/`, et 3 tests de continuité auto-administrables ; livrable : `docs/specs/SPEC_NARRATIVE_SELF.md` + smoke test (gap=G4, étape=4).
gaia-node-4: 
```

</details>