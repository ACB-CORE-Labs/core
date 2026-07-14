# P7 Design Note: True Cross-Spectral Polar vs Field Conjugacy

## 1. Definition of $C_{AB}$ and the Polar Path
In Geometric Algebra, the standard "Clifford polar decomposition" for estimating a rotor $R$ from pairs $(a_i, b_i)$ such that $b_i = R a_i \tilde{R}$ is to form the geometric product sum $C = \sum_i b_i a_i$ (or $b_i \tilde{a}_i$). The rotor is then extracted via the polar decomposition of the multivector: $R = C (\tilde{C} C)^{-1/2}$.

## 2. Applicability to Cl(4,1) Wave Fields (32-vectors)
The above polar decomposition relies on $\tilde{C} C$ being a scalar, which allows the square root and inverse to be well-defined and ensures $R$ is a valid rotor ($R \tilde{R} = 1$). This property holds when $a_i, b_i$ are vectors (grade-1).
However, for general Cl(4,1) multivector fields (which contain mixed grades including spinors, scalars, bivectors, etc.), the product $A \tilde{A}$ is **not** a scalar. Consequently, the multivector sum $C_{AB} = \sum_i B_i \tilde{A}_i$ does not satisfy $\tilde{C} C \in \mathbb{R}$, and the polar decomposition $C_{AB} (\tilde{C}_{AB} C_{AB})^{-1/2}$ is mathematically ill-defined for general 32-vectors. It cannot isolate a valid versor in $Spin(4,1)$.

## 3. Alternative: Linear Map Polar Decomposition
If we define $\mathcal{C}_{AB}$ as a $32 \times 32$ correlation matrix (the Euclidean tensor product), its standard matrix polar decomposition $\mathcal{C}_{AB} = \mathcal{R} \mathcal{S}$ yields an orthogonal matrix $\mathcal{R} \in SO(32)$. However, $Spin(4,1)$ under the sandwich outermorphism is a strict 10-dimensional subspace of $SO(32)$. The matrix $\mathcal{R}$ will almost never be a valid versor sandwich, making this path a geometric dead end.

## 4. Relation to `_field_conjugacy_versor`
Because the analytic polar decomposition does not generalize to arbitrary multivectors in Cl(4,1), the mathematically rigorous way to find the optimal sandwich conjugator is to solve $R A_i - B_i R = 0$ via SVD to find candidate nullspaces, followed by multiplicative Gauss-Newton optimization on the Spin group to minimize the raw sandwich residual. 
This is **exactly** what `_field_conjugacy_versor` does.

## 5. Conclusion (Honesty over Theater)
The "thin wrap" over `_field_conjugacy_versor` is not a lazy shortcut; it is the **only mathematically sound** implementation for general multivector sandwich conjugacy in Cl(4,1). The ADR-0241 language claiming a "Cross-spectral $C_{AB}$ -> Clifford polar decomposition" is a misapplication of a vector-only algorithm to general multivector fields.

Therefore, I recommend **demoting the ADR language** rather than fabricating a broken "polar" path that would fail on multi-grade fields. I will add a test that explicitly proves $C_{AB} (\tilde{C}_{AB} C_{AB})^{-1/2}$ fails to produce a valid versor for mixed-grade fields, cementing `_field_conjugacy_versor` as the true authority.
