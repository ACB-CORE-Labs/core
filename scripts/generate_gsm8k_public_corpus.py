import json
import random
import os

NAMES = ["Alice", "Bob", "Charlie", "David", "Eve", "Frank", "Grace", "Heidi", "Ivan", "Judy", "Mallory", "Nori", "Owen", "Peggy", "Ruth", "Sara", "Trent", "Victor", "Walter"]
UNITS = ["books", "crayons", "apples", "oranges", "stickers", "marbles", "cards", "blocks", "coins", "pencils"]

def generate_transfer_case(case_id, num_entities):
    entities = random.sample(NAMES, num_entities)
    unit = random.choice(UNITS)
    
    initial_state = []
    values = {}
    for e in entities:
        v = random.randint(10, 50)
        initial_state.append({"entity": e, "quantity": {"unit": unit, "value": v}})
        values[e] = v
        
    actor = entities[0]
    target = entities[1]
    
    transfer_amount = random.randint(1, values[actor] - 1)
    
    operations = [{
        "actor": actor,
        "kind": "transfer",
        "operand": {"unit": unit, "value": transfer_amount},
        "target": target
    }]
    
    problem_text = " ".join([f"{e} has {values[e]} {unit}." for e in entities])
    problem_text += f" {actor} hands {transfer_amount} {unit} to {target}."
    
    # randomly ask for someone's total or the overall total
    if random.choice([True, False]):
        problem_text += f" How many {unit} does {target} have?"
        expected_answer = values[target] + transfer_amount
        unknown = {"entity": target, "unit": unit}
        patterns = ["initial_has", "operation_transfer", "question_how_many_entity"]
    else:
        problem_text += f" How many {unit} do they have left?"
        expected_answer = sum(values.values())
        unknown = {"entity": None, "unit": unit}
        patterns = ["initial_has", "operation_transfer", "question_how_many_total"]
        
    return {
        "problem": problem_text,
        "expected_answer": expected_answer,
        "expected_unit": unit,
        "ground_truth_graph": {
            "entities": entities,
            "initial_state": initial_state,
            "operations": operations,
            "unknown": unknown
        },
        "patterns": patterns,
        "notes": "Generated public case exercising transfer operations.",
        "id": case_id
    }

def generate_divide_case(case_id):
    entity = random.choice(NAMES)
    unit = random.choice(UNITS)
    
    divisor = random.randint(2, 5)
    expected_answer = random.randint(2, 20)
    initial_amount = expected_answer * divisor
    
    initial_state = [{"entity": entity, "quantity": {"unit": unit, "value": initial_amount}}]
    operations = [{
        "actor": entity,
        "kind": "divide",
        "operand": {"unit": unit, "value": divisor}
    }]
    
    problem_text = f"{entity} has {initial_amount} {unit}. {entity} splits them evenly into {divisor} groups. How many {unit} does {entity} have?"
    
    return {
        "problem": problem_text,
        "expected_answer": expected_answer,
        "expected_unit": unit,
        "ground_truth_graph": {
            "entities": [entity],
            "initial_state": initial_state,
            "operations": operations,
            "unknown": {"entity": entity, "unit": unit}
        },
        "patterns": ["initial_has", "operation_divide", "question_how_many_entity"],
        "notes": "Generated public case exercising divide operations.",
        "id": case_id
    }

def main():
    random.seed(42)
    os.makedirs("evals/gsm8k_math/public", exist_ok=True)
    
    cases = []
    for i in range(101, 251):
        case_id = f"gma-{i:03d}"
        
        # choose a generator
        choice = random.choice(["transfer", "transfer_multi", "divide"])
        if choice == "transfer":
            cases.append(generate_transfer_case(case_id, 2))
        elif choice == "transfer_multi":
            cases.append(generate_transfer_case(case_id, random.randint(3, 5)))
        elif choice == "divide":
            cases.append(generate_divide_case(case_id))
            
    with open("evals/gsm8k_math/public/cases.jsonl", "w") as f:
        for case in cases:
            f.write(json.dumps(case) + "\n")
            
    print(f"Generated {len(cases)} cases in evals/gsm8k_math/public/cases.jsonl")

if __name__ == "__main__":
    main()
