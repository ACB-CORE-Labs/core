import json
import numpy as np
from packs.compiler import load_mounted_packs
from core.physics.quantity_kernel import embed_quantity
from core.physics.dynamic_manifold import conformal_procrustes
import sys

def embed_graph(g_dict, vocab):
    vectors = []
    
    # 1. Initial State
    for init in g_dict.get("initial_state", []):
        qty = init["quantity"]["value"]
        v_qty = embed_quantity(float(qty))
        
        try:
            v_kind = vocab.get_versor("have")
        except Exception:
            v_kind = np.zeros(32, dtype=np.float64)
            v_kind[0] = 1.0
            
        vectors.append(v_kind)
        vectors.append(v_qty)
        
    # 2. Operations
    for op in g_dict.get("operations", []):
        kind = op["kind"]
        word_map = {
            "compare_multiplicative": "multiply",
            "compare_additive": "add",
            "transfer": "give",
            "add": "add",
            "subtract": "subtract"
        }
        word = word_map.get(kind, kind)
        try:
            v_kind = vocab.get_versor(word)
        except Exception:
            v_kind = np.zeros(32, dtype=np.float64)
            v_kind[0] = 1.0
            v_kind[1] = 1.0
            
        operand = op.get("operand", {})
        val = 1.0
        if "value" in operand:
            val = operand["value"]
        elif "factor" in operand:
            val = operand["factor"]
            
        v_qty = embed_quantity(float(val))
        
        vectors.append(v_kind)
        vectors.append(v_qty)
        
    MAX_VECS = 10
    padded = vectors[:MAX_VECS]
    padding_point = embed_quantity(0.0)
    while len(padded) < MAX_VECS:
        padded.append(padding_point)
        
    return padded

def main():
    print("Loading vocab...")
    # Load base math vocab
    vocab = load_mounted_packs(["en_mathematics_logic_v1", "en_core_math_v1", "en_core_relations_v1", "en_core_relations_v2", "en_core_relations_v3"])
    
    graphs_path = "sme_graphs.jsonl"
    labels_path = "labels.jsonl"
    
    cases = []
    with open(graphs_path, "r") as f:
        for line in f:
            cases.append(json.loads(line))
    
    # Use subset for speed
    cases = cases[:20]
            
    # Embed blind
    print(f"Embedding {len(cases)} cases blind of labels...")
    embeddings = []
    case_ids = []
    for c in cases:
        emb = embed_graph(c["graph"], vocab)
        embeddings.append(emb)
        case_ids.append(c["id"])
        
    # Align pairs
    print("Computing Procrustes alignment residuals...")
    n = len(cases)
    residuals = np.zeros((n, n))
    
    for i in range(n):
        print(f"Aligning case {i}/{n}...", flush=True)
        for j in range(i, n):
            try:
                _, res = conformal_procrustes(embeddings[i], embeddings[j])
            except ValueError:
                res = 1000.0
            except Exception:
                res = 1000.0
                
            residuals[i, j] = res
            residuals[j, i] = res
            
    # Now load labels and score
    print("Loading labels for evaluation...")
    id_to_label = {}
    with open(labels_path, "r") as f:
        for line in f:
            l = json.loads(line)
            id_to_label[l["id"]] = l["label"]
            
    labels = [id_to_label[cid] for cid in case_ids]
    
    # Evaluate
    same_res = []
    cross_res = []
    
    for i in range(n):
        for j in range(i + 1, n):
            res = residuals[i, j]
            if labels[i] == labels[j]:
                same_res.append(res)
            else:
                cross_res.append(res)
                
    same_mean = np.mean(same_res) if same_res else 0.0
    cross_mean = np.mean(cross_res) if cross_res else 0.0
    
    print(f"\nSame-structure residual (mean): {same_mean:.6f}")
    print(f"Cross-structure residual (mean): {cross_mean:.6f}")
    print(f"Separability margin: {cross_mean - same_mean:.6f}")
    
    if cross_mean > same_mean * 2 and same_mean < 1.0:
        print("\nVERDICT: GO")
    else:
        print("\nVERDICT: NO-GO")

if __name__ == "__main__":
    main()
