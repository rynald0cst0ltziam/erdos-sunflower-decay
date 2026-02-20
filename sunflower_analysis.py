#!/usr/bin/env python3
import itertools
import collections
import math
import sys

def analyze_family(family, n, k):
    """
    Analyze a family of n-sets for sunflower-freeness and spreadness.
    """
    m = len(family)
    if m == 0: return
    
    # 1. Sunflower Check (k=3)
    sunflowers = []
    for i in range(m):
        for j in range(i + 1, m):
            kernel = family[i] & family[j]
            for l in range(j + 1, m):
                if (family[i] & family[l] == kernel) and (family[j] & family[l] == kernel):
                    sunflowers.append((i, j, l))
    
    print(f"Family Size: {m}")
    print(f"Sunflower-free: {'YES' if not sunflowers else 'NO'}")
    if sunflowers:
        print(f"Number of 3-sunflowers: {len(sunflowers)}")
        
    # 2. Spreadness Check
    # A family is kappa-spread if for all S, |F_S| <= kappa^{-|S|} |F|
    # i.e. kappa <= (|F| / |F_S|)^{1/|S|}
    # We want to find the MINIMUM such kappa over all S.
    
    subsets_counts = collections.defaultdict(int)
    for s in family:
        # All proper non-empty subsets
        for r in range(1, n):
            for sub in itertools.combinations(sorted(list(s)), r):
                subsets_counts[sub] += 1
                
    min_kappa = float('inf')
    worst_S = None
    
    for S, count in subsets_counts.items():
        # count / m <= kappa^-|S|  =>  m / count >= kappa^|S|  => (m/count)^(1/|S|) >= kappa
        kappa = (m / count)**(1.0 / len(S))
        if kappa < min_kappa:
            min_kappa = kappa
            worst_S = S
            
    print(f"Spreadness (min kappa): {min_kappa:.4f}")
    if worst_S:
        print(f"Worst subset: {worst_S} (appears in {subsets_counts[worst_S]} sets)")
    
    # Expected threshold from ALWZ: kappa > C log n
    print(f"C = kappa / log2(n) = {min_kappa / math.log2(n) if n > 1 else 0:.4f}")

if __name__ == "__main__":
    import ast
    data = sys.stdin.read()
    if data.strip():
        family_list = ast.literal_eval(data)
        family = [set(s) for s in family_list]
        analyze_family(family, 3, 3)
