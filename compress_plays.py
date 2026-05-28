"""
compress_csv.py  –  Encode binary hand columns as a single integer, reducing space on repository.

Usage:
    python compress_csv.py input.csv output.csv

The 22 columns before "Result" are treated as a binary number (leftmost = MSB)
and collapsed into a single "Hand" integer column. Output is: Hand,Result
"""

import sys
import pandas as pd

def compress(input_path: str, output_path: str) -> None:
    print(f"Reading {input_path} ...")
    df = pd.read_csv(input_path)

    # All columns except Result are the hand bits
    hand_cols = [c for c in df.columns if c != "Result"]

    print(f"Encoding {len(hand_cols)} bit-columns into a single integer ...")

    # Build a power-of-2 weight for each column (leftmost col = highest bit)
    n = len(hand_cols)
    powers = [2 ** (n - 1 - i) for i in range(n)]

    # Matrix multiply: each row of bits · powers vector = hand integer
    hand_values = df[hand_cols].values @ powers

    out = pd.DataFrame({"Hand": hand_values, "Result": df["Result"]})

    print(f"Writing {output_path} ...")
    out.to_csv(output_path, index=False)
    print("Done.")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python compress_csv.py <input.csv> <output.csv>")
        sys.exit(1)
    compress(sys.argv[1], sys.argv[2])