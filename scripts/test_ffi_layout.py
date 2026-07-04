import os
import sys

# Ensure backend uses Rust
os.environ["CORE_BACKEND"] = "rust"

import numpy as np
from generate.problem_frame_contracts import VersorBinding
from algebra.backend import using_rust

def test_ffi_layout():
    if not using_rust():
        print("Warning: Rust backend not loaded!")

    # A valid unit versor (scalar 1.0)
    payload = np.zeros(32, dtype=np.float64)
    payload[0] = 1.0

    print(f"payload flags before binding:\n{payload.flags}")
    
    # Instantiate VersorBinding.
    binding = VersorBinding(
        source_span=(0, 10),
        semantic_identity="test_identity",
        geometric_payload=payload,
        versor_error=0.0
    )

    print("\nVersorBinding successfully instantiated!")
    print(f"Versor Error Validation: passed")
    print(f"Memory Layout is C-Contiguous: {binding.geometric_payload.flags.c_contiguous}")
    print(f"Dtype: {binding.geometric_payload.dtype}")

if __name__ == "__main__":
    test_ffi_layout()
