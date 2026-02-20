#!/usr/bin/env python3
"""
Sunflower Engine V2 - High Performance Search for Sunflower-free Families.
Using SAT + Batch Cutting + Kernel-based Detection.

Problem: Find max size of family F of n-sets such that no k sets form a sunflower.
Conjecture: |F| < C^n.
"""

import sys
import time
import json
import argparse
import itertools
import collections
from pysat.solvers import Solver, SolverNames
from pysat.formula import CNF, IDPool
from pysat.card import CardEnc, EncType

def log(msg):
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)

class SunflowerEngine:
    def __init__(self, n, k, U, solver_name="glucose3"):
        self.n = n
        self.k = k
        self.U = U
        self.all_sets = list(itertools.combinations(range(U), n))
        self.num_all = len(self.all_sets)
        self.vpool = IDPool()
        self.cnf = CNF()
        self.solver_name = solver_name
        
        # Map each set to an ID
        self.set_to_id = {s: i for i, s in enumerate(self.all_sets)}
        
        # Precompute kernels for each set to speed up detection
        # kernel_map[K] = [list of set_ids containing K]
        log(f"Precomputing kernels for {self.num_all} sets...")
        self.kernel_map = collections.defaultdict(list)
        for i, s_tuple in enumerate(self.all_sets):
            s = set(s_tuple)
            # All proper subsets are potential kernels
            for r in range(n):
                for K in itertools.combinations(s_tuple, r):
                    self.kernel_map[K].append(i)
        log(f"Finished precomputing {len(self.kernel_map)} potential kernels.")

    def find_sunflowers(self, active_ids):
        """
        Find sunflowers in the current active family.
        A sunflower with kernel K exists if there are k sets containing K 
        whose 'petals' (S \ K) are disjoint.
        """
        active_set = set(active_ids)
        sunflowers = []
        
        # Check each potential kernel
        for K, set_ids in self.kernel_map.items():
            # Only consider sets in the current family
            family_at_K = [sid for sid in set_ids if sid in active_set]
            if len(family_at_K) < self.k:
                continue
            
            # Extract petals
            petals = []
            K_set = set(K)
            for sid in family_at_K:
                petals.append((set(self.all_sets[sid]) - K_set, sid))
            
            # Find k disjoint petals (matching problem)
            # For small k and n, we can use a simple recursive search
            found_petals_ids = self._find_disjoint(petals, self.k)
            if found_petals_ids:
                sunflowers.append(found_petals_ids)
                
        return sunflowers

    def _find_disjoint(self, petals_with_ids, target_k):
        """Find target_k disjoint petals using backtracking."""
        def backtrack(start_idx, current_petals_ids, combined_elements):
            if len(current_petals_ids) == target_k:
                return current_petals_ids
            
            for i in range(start_idx, len(petals_with_ids)):
                petal, sid = petals_with_ids[i]
                if petal.isdisjoint(combined_elements):
                    res = backtrack(i + 1, current_petals_ids + [sid], combined_elements | petal)
                    if res:
                        return res
            return None
            
        return backtrack(0, [], set())

    def solve(self, target_size, max_batches=1000):
        """Search for a family of target_size using SAT + Batch Cutting."""
        # Initial constraint: exactly target_size sets
        lits = [i + 1 for i in range(self.num_all)]
        self.cnf.extend(CardEnc.equals(lits, bound=target_size, vpool=self.vpool, encoding=EncType.seqcounter).clauses)
        
        with Solver(name=self.solver_name, bootstrap_with=self.cnf) as S:
            batch = 0
            while batch < max_batches:
                batch += 1
                start_solve = time.time()
                if not S.solve():
                    log(f"UNSAT: No sunflower-free family of size {target_size} exists in U={self.U}")
                    return None
                
                model = S.get_model()
                active_ids = [i for i in range(self.num_all) if model[i] > 0]
                
                # Check for sunflowers
                sunflowers = self.find_sunflowers(active_ids)
                if not sunflowers:
                    log(f"SUCCESS: Found sunflower-free family of size {target_size}!")
                    return [self.all_sets[sid] for sid in active_ids]
                
                # Batch block
                for sf in sunflowers:
                    # Block this specific sunflower: at least one set must be OUT
                    S.add_clause([- (sid + 1) for sid in sf])
                
                log(f"Batch {batch}: Found and blocked {len(sunflowers)} sunflowers. (Solve time: {time.time()-start_solve:.2f}s)")
                
            log("Reached max batches without finding a solution.")
            return None

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", type=int, default=3, help="Set size")
    parser.add_argument("-k", type=int, default=3, help="Sunflower size")
    parser.add_argument("-U", type=int, default=7, help="Universe size")
    parser.add_argument("--target", type=int, default=20, help="Target family size")
    parser.add_argument("--solver", type=str, default="glucose3", help="SAT solver name")
    args = parser.parse_args()

    log(f"Sunflower Engine: n={args.n}, k={args.k}, U={args.U}, target={args.target}")
    engine = SunflowerEngine(args.n, args.k, args.U, solver_name=args.solver)
    
    # Try reaching target
    result = engine.solve(args.target)
    if result:
        print("\nFound Family:")
        for s in result:
            print(sorted(list(s)))
        
        # Save to file
        out_file = f"sunflower_n{args.n}_k{args.k}_m{args.target}.json"
        with open(out_file, "w") as f:
            json.dump({
                "n": args.n,
                "k": args.k,
                "U": args.U,
                "m": args.target,
                "family": [list(s) for s in result]
            }, f, indent=2)
        log(f"Saved to {out_file}")
    else:
        log("Failed to find a family of requested size.")

if __name__ == "__main__":
    main()
