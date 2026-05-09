# Project 6: Optimal Deferral Strategies Under Budget Constraints

## Research Overview

**Core Question:** How can AI systems learn to recognize situations where human judgment is most valuable relative to the oversight cost?

**Problem Statement:** As AI systems handle increasingly complex decisions, human oversight becomes a scarce resource. Not every AI decision can be reviewed — oversight budgets are finite (time, attention, expertise). The critical challenge is developing algorithms that optimally allocate human review to the decisions where it matters most, maximizing oversight value per unit of human effort.

---

## 1. Research Questions & Hypotheses

### Primary Research Questions

**RQ1:** Can AI systems learn deferral policies that outperform fixed-threshold baselines under constrained oversight budgets?

**RQ2:** How does the optimal deferral strategy change as the oversight budget varies from 1% to 50% of total decisions?

**RQ3:** What decision features best predict the marginal value of human review (i.e., the gap between AI-only and human-corrected outcomes)?

### Hypotheses

- **H1:** Learned deferral policies using uncertainty + decision-impact features will achieve ≥15% higher outcome quality than confidence-threshold baselines at equal budget levels.
- **H2:** The relationship between budget and oversight value follows a diminishing-returns curve, with an "elbow" point beyond which additional oversight yields minimal improvement.
- **H3:** Decision novelty (distributional distance from training data) is a stronger predictor of deferral value than raw model uncertainty.
- **H4:** Optimal deferral rates are non-stationary — they should increase during distribution shifts and decrease during stable periods.

---

## 2. Theoretical Framework

### 2.1 The Deferral Decision as Optimization

Define the deferral problem formally:

- Let **D** = set of decisions the AI system must make
- Let **B** = oversight budget (fraction of D that humans can review)
- Let **V(d)** = value of human review for decision d (outcome improvement)
- Let **C(d)** = cost of deferring decision d (delay, cognitive load on human)

**Objective:** Learn a deferral policy π: D → {0,1} that maximizes:

```
max_π Σ_{d∈D} π(d) · V(d)   subject to   Σ_{d∈D} π(d) ≤ B
```

### 2.2 Value-of-Information Framework

The marginal value of human review for decision d decomposes into:

1. **Error correction value:** P(AI wrong on d) × impact(d)
2. **Calibration value:** Information gained about AI reliability in region around d
3. **Learning value:** Training signal for improving future AI decisions
4. **Trust maintenance value:** Human confidence preserved by reviewing consequential decisions

### 2.3 Connection to Existing Theory

- **Learning to Defer (Madras et al., 2018; Mozannar & Sontag, 2020):** Extends to budget-constrained settings with non-uniform costs
- **Selective Prediction (El-Yaniv & Wiener, 2010):** Abstention with fixed coverage guarantees
- **Active Learning:** Budget allocation as sequential decision problem
- **Multi-armed Bandits:** Exploration-exploitation tradeoff in deferral policy learning

---

## 3. Proposed Algorithms

### 3.1 Algorithm 1: Budget-Constrained Deferral via Learned Value Estimation (BC-DVE)

**Approach:** Train a "deferral value estimator" that predicts V(d) for each decision, then defer the top-B decisions by estimated value.

**Architecture:**
1. Feature extraction: model uncertainty (epistemic + aleatoric), decision stakes, input novelty, task complexity
2. Value prediction head: regression model trained on historical (decision, human-correction) pairs
3. Budget-aware ranking: rank decisions by predicted V(d), defer top B

**Training procedure:**
- Phase 1: Collect data from uniform-random deferral policy (exploration)
- Phase 2: Train value estimator on observed V(d) values
- Phase 3: Deploy learned policy, continue updating with new observations (exploitation)
- Use importance-weighted corrections for off-policy learning

### 3.2 Algorithm 2: Contextual Bandit Deferral (CBD)

**Approach:** Frame deferral as a contextual bandit where the context is the decision features, the action is defer/not-defer, and the reward is outcome quality.

**Key innovation:** Thompson Sampling variant that naturally handles the exploration-exploitation tradeoff in learning when to defer.

**Steps:**
1. Maintain posterior distribution over deferral value for each feature region
2. Sample from posterior to decide deferral (explore uncertain regions)
3. Update posterior with observed outcomes
4. Budget enforcement via Lagrangian relaxation

### 3.3 Algorithm 3: Dynamic Budget Allocation with Change Detection (DBA-CD)

**Approach:** Adapt deferral rate dynamically based on detected distribution shifts or performance degradation.

**Mechanism:**
1. Monitor AI system performance on deferred (human-reviewed) decisions
2. Use CUSUM or Page-Hinkley change detection on error rates
3. When shift detected: temporarily increase deferral rate (spend budget faster)
4. When stable: decrease deferral rate (conserve budget)
5. Maintains a "budget reserve" for unexpected situations

### 3.4 Algorithm 4: Hierarchical Deferral with Triage Levels

**Approach:** Multi-level deferral system matching oversight depth to decision criticality.

**Levels:**
- Level 0: AI decides autonomously (no budget spent)
- Level 1: Quick human spot-check — 30-second review (low budget cost)
- Level 2: Standard human review — 2-5 minute review (medium budget cost)
- Level 3: Deep human deliberation — expert panel (high budget cost)

**Budget accounting:** Each level has different cost; optimize total value under total budget constraint.

---

## 4. Experimental Design

### 4.1 Study 1: Simulated Decision Environments

**Objective:** Compare algorithms under controlled conditions with known ground truth.

**Environments:**
1. **Medical triage simulation:** AI recommends treatment priorities; human reviews selected cases. Known error distributions, clear outcome metrics.
2. **Content moderation simulation:** AI flags content; human reviews subset. Varying difficulty levels, evolving policy.
3. **Financial risk assessment:** AI scores loan applications; human reviews edge cases. Ground truth available retrospectively.

**Independent variables:**
- Budget level B ∈ {0.01, 0.05, 0.10, 0.20, 0.50}
- Distribution shift severity (none, mild, severe)
- Decision complexity distribution
- Algorithm choice (4 proposed + 3 baselines)

**Baselines:**
1. Random deferral (defer random B fraction)
2. Confidence threshold (defer lowest-confidence B fraction)
3. Fixed rules (defer based on domain-specific rules)

**Dependent variables:**
- Overall decision quality (accuracy, F1, or domain-specific metric)
- Regret vs. oracle deferral policy
- Budget utilization efficiency (value gained per unit budget spent)
- Adaptation speed after distribution shift

**Design:** 50 simulated runs per condition. 2×5×3×7 factorial = 210 conditions × 50 runs = 10,500 simulation runs.

### 4.2 Study 2: Human-in-the-Loop Experiment

**Objective:** Validate with real human reviewers to capture cognitive and behavioral effects algorithms alone miss.

**Participants:** N=120 (power analysis for medium effect size d=0.5, α=0.05, power=0.80, accounting for attrition).

**Task:** Participants serve as human reviewers for an AI content classification system. They review AI decisions that are deferred to them under different deferral policies.

**Conditions (between-subjects, N=30 per group):**
1. Random deferral
2. Confidence-threshold deferral
3. BC-DVE (best-performing learned algorithm from Study 1)
4. DBA-CD (adaptive algorithm)

**Protocol:**
- 60-minute session: training (10 min), task blocks (40 min), debrief (10 min)
- 200 total decisions per session, 20% budget (40 human reviews)
- Decisions include planted errors of varying difficulty
- Measure: error detection rate, review time, self-reported workload (NASA-TLX), decision confidence

**Key measurements:**
- Does the deferral algorithm successfully route the "right" decisions to humans?
- Do participants detect more errors when the algorithm pre-selects high-value deferrals?
- Does review quality degrade over time (fatigue interaction)?
- Subjective experience: do participants feel the system is "wasting their time" or "showing them the important ones"?

### 4.3 Study 3: Longitudinal Learning Dynamics

**Objective:** Test H4 — how optimal deferral strategies evolve over time as both AI and human adapt.

**Design:** 10-session longitudinal study (same participants, spread over 3 weeks).

**Participants:** N=60 (subset from Study 2 who consent to longitudinal participation).

**Manipulation:** 
- Group A (N=30): Static deferral policy (frozen after initial calibration)
- Group B (N=30): Adaptive deferral policy (continuously updates based on human performance)

**Measures per session:**
- Human error detection rate
- Human review time per decision
- AI system accuracy on non-deferred decisions
- Deferral policy entropy (diversity of deferred decisions)
- Trust survey (Jian et al. trust scale)

---

## 5. Feature Engineering for Deferral Value Prediction

### 5.1 Proposed Feature Categories

| Category | Features | Rationale |
|----------|----------|-----------|
| **Model Uncertainty** | Predictive entropy, MC-dropout variance, ensemble disagreement | Core signal for AI confidence |
| **Input Novelty** | Mahalanobis distance, k-NN distance in embedding space, OOD score | Decisions unlike training data may need human review |
| **Decision Stakes** | Outcome severity, reversibility, affected population size | High-stakes decisions warrant more oversight |
| **Temporal Context** | Time since last deferral, recent error rate, session fatigue estimate | Budget pacing and reviewer state |
| **Task Complexity** | Input length, number of relevant factors, ambiguity score | Complex decisions may benefit more from human input |
| **Historical Performance** | AI accuracy in similar decisions, human correction rate in region | Empirical deferral value signal |

### 5.2 Feature Importance Analysis Plan

- SHAP analysis on the deferral value estimator
- Ablation studies: remove one feature category at a time, measure performance drop
- Interaction analysis: which feature combinations are most predictive?

---

## 6. Evaluation Metrics

### 6.1 Primary Metrics

1. **Oversight Efficiency Ratio (OER):** Quality improvement per unit of budget spent
   ```
   OER = (Q_deferred - Q_autonomous) / B
   ```
2. **Regret vs. Oracle:** Gap between learned policy and optimal hindsight policy
3. **Budget Utilization Curve:** Quality as function of budget level (to find the "elbow")

### 6.2 Secondary Metrics

4. **Deferral Precision:** Fraction of deferred decisions where human actually changed the outcome
5. **Coverage of Critical Errors:** Fraction of high-impact AI errors that were caught by deferral
6. **Adaptation Latency:** Time to adjust deferral policy after distribution shift
7. **Human Reviewer Satisfaction:** Perceived usefulness of deferred decisions (Likert scale)

### 6.3 Fairness Metrics

8. **Demographic Parity of Deferral:** Ensure deferral rates don't systematically vary across protected groups
9. **Equal Coverage:** Critical error detection rates should be comparable across subpopulations

---

## 7. Resource Requirements & Timeline

### 7.1 Timeline

| Phase | Duration | Activities |
|-------|----------|------------|
| **Phase 1: Foundation** | Weeks 1-4 | Literature review, algorithm implementation, simulation environment setup |
| **Phase 2: Simulation** | Weeks 5-8 | Study 1 — simulated experiments, algorithm comparison |
| **Phase 3: Refinement** | Weeks 9-10 | Algorithm tuning based on simulation results, IRB preparation |
| **Phase 4: Human Studies** | Weeks 11-16 | Study 2 — human-in-the-loop experiment |
| **Phase 5: Longitudinal** | Weeks 17-22 | Study 3 — longitudinal learning dynamics |
| **Phase 6: Analysis** | Weeks 23-26 | Data analysis, paper writing |

### 7.2 Resource Estimates

- **Compute:** ~500 GPU-hours for simulation experiments (standard cloud instance)
- **Participants:** 120 for Study 2, 60 for Study 3
- **Compensation:** $20/hr × ~2 hrs average = ~$40/participant, ~$7,200 total
- **Software:** Custom experimental platform (Python/JS), integration with existing AI models
- **Personnel:** 1 PI (20% time), 1 research coordinator (50% time), 1 data analyst (30% time)

### 7.3 Ethics

- IRB approval required for Studies 2 and 3
- Informed consent for all human participants
- No deceptive elements — participants know they're evaluating AI deferral policies
- Data anonymization protocols for behavioral data
- Debriefing includes explanation of which deferral policy they experienced

---

## 8. Expected Contributions

1. **Algorithmic:** Novel budget-constrained deferral algorithms that outperform simple baselines
2. **Empirical:** First human-subjects study of how deferral policy design affects real oversight quality
3. **Practical:** Design guidelines for when to defer and at what review depth
4. **Theoretical:** Formal framework connecting deferral value to model uncertainty, decision stakes, and input novelty
5. **Policy-relevant:** Evidence-based recommendations for oversight budget allocation in AI governance

---

## 9. Connections to Other HumanJi Projects

- **Project 1 (Cognitive Load):** Deferral policies must account for reviewer cognitive state — feeds into our temporal context features
- **Project 4 (Learning Curves):** Longitudinal Study 3 directly builds on learning curve findings — do deferral policies improve as humans learn?
- **Project 5 (Interface Design):** How deferred decisions are presented to reviewers affects oversight quality — coordinate on interface design
- **Project 7 (Temporal Dynamics):** Dynamic budget allocation (Algorithm 3) interacts with temporal patterns in oversight effectiveness

---

## 10. Risk Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Simulation results don't transfer to real humans | Medium | High | Start human studies early (pilot); design simulations with realistic cognitive constraints |
| Insufficient participant recruitment | Low | High | Partner with university participant pool; offer competitive compensation |
| Algorithms overfit to specific decision domains | Medium | Medium | Test across 3+ domains; validate with held-out domain |
| Budget enforcement is too rigid for real-world use | Low | Medium | Include "soft budget" variant with penalty for overuse rather than hard cap |
| Fairness issues in deferral patterns | Medium | High | Include fairness metrics from start; run disparity audits on all algorithms |
