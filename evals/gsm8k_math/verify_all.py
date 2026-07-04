#!/usr/bin/env python3
import json
import sys
from collections import defaultdict
from pathlib import Path

# Add the workspace root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from generate.math_parser import parse_problem, ParseError
from generate.math_problem_graph import graph_from_dict
from generate.math_solver import solve, SolveError
from generate.math_verifier import verify

def verify_cases():
    root = Path(__file__).resolve().parents[2]
    dev_path = root / "evals/gsm8k_math/dev/cases.jsonl"
    public_path = root / "evals/gsm8k_math/public/cases.jsonl"
    
    cases = []
    for path in (dev_path, public_path):
        if not path.exists():
            print(f"Error: file not found at {path}")
            return False
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    cases.append(json.loads(line))
                    
    if len(cases) != 200:
        print(f"Error: expected exactly 200 cases total, got {len(cases)}")
        return False
        
    passed = 0
    for case in cases:
        case_id = case.get("id", "unknown")
        problem = case["problem"]
        expected_ans = case["expected_answer"]
        expected_unit = case["expected_unit"]
        gt_dict = case["ground_truth_graph"]
        
        try:
            # 1. Parse (M1)
            parsed_graph = parse_problem(problem)
            
            # Match GT graph
            gt_graph_obj = graph_from_dict(gt_dict)
            if parsed_graph.canonical_bytes() != gt_graph_obj.canonical_bytes():
                print(f"FAIL {case_id}: Graph canonical bytes mismatch.")
                continue
                
            # 2. Solve (M2)
            trace = solve(parsed_graph)
            if trace.answer_value != expected_ans:
                print(f"FAIL {case_id}: Answer value mismatch. Expected {expected_ans}, got {trace.answer_value}")
                continue
                
            # Match unit
            if trace.answer_unit != expected_unit:
                print(f"FAIL {case_id}: Answer unit mismatch. Expected {expected_unit!r}, got {trace.answer_unit!r}")
                continue
                
            # 3. Verify (M3)
            verdict = verify(parsed_graph, trace)
            if not verdict.passed:
                print(f"FAIL {case_id}: Verification failed - {verdict.error_message}")
                continue
                
            passed += 1
                
        except (ParseError, SolveError, Exception) as e:
            print(f"FAIL {case_id}: Exception raised - {type(e).__name__}: {e}")
            continue
            
    print(f"\n--- Verification Stats ---")
    print(f"Cases parsed, solved, and verified successfully: {passed}/200")
    
    if passed == 200:
        print("\n200/200 OK")
        return True
    else:
        print(f"\nFAIL: Only {passed}/200 cases passed verification.")
        return False

if __name__ == "__main__":
    success = verify_cases()
    sys.exit(0 if success else 1)
