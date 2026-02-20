#!/usr/bin/env python3
import sys
import ast
from sunflower_analysis import analyze_family

def main():
    if len(sys.argv) < 2:
        print("Usage: analyze_latest.py <output_file>")
        return
        
    filename = sys.argv[1]
    with open(filename, "r") as f:
        lines = f.readlines()
        
    # Find the start of the family output
    # Families are printed after "SUCCESS" or "FAILURE"
    family = []
    found_marker = False
    for line in lines:
        if "SUCCESS" in line or "FAILURE" in line:
            found_marker = True
            continue
        if found_marker:
            try:
                s = ast.literal_eval(line.strip())
                if isinstance(s, list):
                    family.append(set(s))
            except:
                continue
                
    if family:
        print(f"Analyzing family of size {len(family)} from {filename}")
        n = len(list(family)[0]) if family else 3
        analyze_family(family, n, 3) # Assuming k=3
    else:
        print("No family found in output file.")

if __name__ == "__main__":
    main()
