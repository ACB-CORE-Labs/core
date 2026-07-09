#!/bin/bash
SCRATCH=${1:-/var/folders/kg/5xbm28qd7jl55j7lv3p001f40000gn/T/grok-goal-5bb2b72e8d0e/implementer}
mkdir -p "$SCRATCH"
echo "Capturing spine evidence to $SCRATCH/spine_tests.log"
.venv/bin/python -m pytest -v -s -k 'anti_unifier_root_aware or depth_canonical_direct or pipeline_node_depths_emission or graph_anti_unify or contemplate_depth or teaching_contemplate_depth' tests/test_oov_pipeline.py 2>&1 | tee "$SCRATCH/spine_tests.log"
echo "Re-run"
.venv/bin/python -m pytest -v -s -k 'anti_unifier_root_aware or depth_canonical_direct or pipeline_node_depths_emission or graph_anti_unify' tests/test_oov_pipeline.py 2>&1 | tee -a "$SCRATCH/spine_tests.log"
echo "Done. Check for root forms, nid, non-empty ctx, id equality in log."
