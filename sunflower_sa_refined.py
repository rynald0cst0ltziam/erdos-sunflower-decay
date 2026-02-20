#!/usr/bin/env python3
import random
import time
import argparse
import math
from collections import defaultdict

class SunflowerLocalSearch:
    def __init__(self, n, k, m, U):
        self.n = n
        self.k = k
        self.m = m
        self.U = U
        self.sets = []
        self.intersections = [[0]*m for _ in range(m)]
        # Map kernel -> list of pairs (i, j)
        self.kernel_to_pairs = defaultdict(set)
        self.energy = 0
        self.best_sets = []
        
    def to_mask(self, s):
        mask = 0
        for x in s:
            mask |= (1 << x)
        return mask

    def get_random_set(self):
        s = random.sample(range(self.U), self.n)
        return self.to_mask(s)

    def calculate_energy(self):
        self.energy = 0
        self.kernel_to_pairs.clear()
        for i in range(self.m):
            for j in range(i + 1, self.m):
                K = self.sets[i] & self.sets[j]
                self.kernel_to_pairs[K].add((i, j))
        
        for K, pairs in self.kernel_to_pairs.items():
            adj = defaultdict(set)
            nodes = set()
            for i, j in pairs:
                adj[i].add(j)
                adj[j].add(i)
                nodes.add(i)
                nodes.add(j)
            
            node_list = list(nodes)
            for idx1 in range(len(node_list)):
                u = node_list[idx1]
                for idx2 in range(idx1 + 1, len(node_list)):
                    v = node_list[idx2]
                    if v in adj[u]:
                        for idx3 in range(idx2 + 1, len(node_list)):
                            w = node_list[idx3]
                            if w in adj[u] and w in adj[v]:
                                self.energy += 1

    def run(self, max_steps=1000000):
        seen = set()
        while len(self.sets) < self.m:
            s = self.get_random_set()
            if s not in seen:
                seen.add(s)
                self.sets.append(s)
        
        self.calculate_energy()
        best_energy = self.energy
        self.best_sets = list(self.sets)
        
        print(f"Initial energy: {self.energy}")
        
        temp = 1.0
        cooling = 0.99999
        start_time = time.time()
        
        for step in range(max_steps):
            if self.energy == 0:
                return self.sets
            
            idx = random.randrange(self.m)
            old_mask = self.sets[idx]
            new_mask = self.get_random_set()
            while new_mask in seen:
                new_mask = self.get_random_set()
            
            loss = 0
            for j in range(self.m):
                if j == idx: continue
                K_ij = self.sets[idx] & self.sets[j]
                for l in range(j + 1, self.m):
                    if l == idx: continue
                    if (self.sets[idx] & self.sets[l] == K_ij) and (self.sets[j] & self.sets[l] == K_ij):
                        loss += 1
            
            gain = 0
            for j in range(self.m):
                if j == idx: continue
                K_new_j = new_mask & self.sets[j]
                for l in range(j + 1, self.m):
                    if l == idx: continue
                    if (new_mask & self.sets[l] == K_new_j) and (self.sets[j] & self.sets[l] == K_new_j):
                        gain += 1
            
            delta = gain - loss
            if delta <= 0 or (temp > 0 and random.random() < math.exp(-delta / temp)):
                seen.remove(old_mask)
                self.sets[idx] = new_mask
                seen.add(new_mask)
                self.energy += delta
                if self.energy < best_energy:
                    best_energy = self.energy
                    self.best_sets = list(self.sets)
            
            temp *= cooling
            if step % 10000 == 0:
                elapsed = time.time() - start_time
                print(f"Step {step}, Energy {self.energy}, Best {best_energy}, Temp {temp:.6f}, Time {elapsed:.1f}s", flush=True)

        return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", type=int, default=3)
    parser.add_argument("-m", type=int, default=19)
    parser.add_argument("-U", type=int, default=20)
    parser.add_argument("--steps", type=int, default=1000000)
    args = parser.parse_args()
    
    ls = SunflowerLocalSearch(args.n, 3, args.m, args.U)
    res = ls.run(max_steps=args.steps)
    if res:
        print("SUCCESS")
        sets = res
    else:
        print("FAILURE")
        sets = ls.best_sets
    
    for s in sets:
        l = []
        for b in range(args.U):
            if (s >> b) & 1: l.append(b)
        print(sorted(l))
