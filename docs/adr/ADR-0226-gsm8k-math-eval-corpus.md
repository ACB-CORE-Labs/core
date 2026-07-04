# ADR 0226: GSM8K Math Evaluation Corpus Generation

## Status
Accepted

## Context
The CORE cognitive engine uses a mathematically pure $Cl(4,1)$ Conformal Geometric Algebra (CGA) substrate to solve grade-school math problems without stochastic text-parsing heuristics. To accurately benchmark parser, solver, and verifier correctness, we require an evaluation corpus that exercises these components thoroughly. However, the original upstream GSM8K dataset contains stochastic natural language variations that are out-of-distribution for our strictly typed CORE grammar. Furthermore, using the standard GSM8K test set during active development risks contaminating our holdout set.

## Decision
We decided to author an original, synthetic 200-case GSM8K-style math evaluation corpus divided into:
- **Dev Set**: 50 cases authored manually to establish structural templates aligned perfectly with our CORE grammar (e.g., `transfer`, `divide`, `proportional_change.decrease_to_fraction`).
- **Public Set**: 150 cases synthetically generated using a Python script (`scripts/generate_gsm8k_public_corpus.py`) configured to sample from the structural templates of the dev set while randomizing entities, numerical values, and units.

To validate correctness, we implemented an automated verification pipeline (`evals/gsm8k_math/verify_all.py`) that executes the M1 (Parse), M2 (Solve), and M3 (Verification) pipelines on all 200 cases. 

## Consequences
- **Positive:** Developers have an immediate, unpolluted feedback loop to confirm parser/solver accuracy without revealing the actual GSM8K holdout set. We guarantee that the generated text rigorously matches the geometric topologies supported by the engine.
- **Negative:** The generated public set has limited linguistic diversity compared to real human-authored text, potentially hiding parser brittleness to novel phrasing. We accept this trade-off in the current architectural phase.
