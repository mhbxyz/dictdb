#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Benchmarking Script for DictDB Query Performance
================================================

This script benchmarks the performance of a simple equality select query on a large dataset
using DictDB. It measures the average execution time (over a number of iterations) for three scenarios:
    - Without any index.
    - With a hash index on the 'age' field.
    - With a sorted index on the 'age' field.

The script uses cProfile to profile the overall performance of the benchmark run.

Usage:
    $ python scripts/benchmark.py [--rows 10000] [--iterations 10] [--age 30] [--seed 42] [--profile] [--json-out results.json]

Author: Your Name
Date: YYYY-MM-DD
"""

import argparse
import cProfile
import json
import random
from time import perf_counter
from typing import Optional, TypedDict

from dictdb import Condition, Table, configure_logging


class BenchmarkResult(TypedDict):
    """
    Type alias for benchmark results.

    Keys:
        without_index: Average query execution time (in seconds) without an index.
        hash_index: Average query execution time (in seconds) with a hash index.
        sorted_index: Average query execution time (in seconds) with a sorted index.
    """

    without_index: float
    hash_index: float
    sorted_index: float


def populate_table(n: int, index_type: Optional[str] = None) -> Table:
    """
    Populates a new DictDB Table with n records.

    Each record has an 'id', 'name', and 'age'. If index_type is provided,
    an index on the 'age' field is created with the specified type ("hash" or "sorted").

    :param n: Number of records to insert.
    :param index_type: Type of index to create ("hash" or "sorted"), or None.
    :return: A populated Table instance.
    """
    table = Table(
        "benchmark_table", primary_key="id", schema={"id": int, "name": str, "age": int}
    )
    for i in range(1, n + 1):
        age = random.randint(20, 60)
        table.insert({"id": i, "name": f"Name{i}", "age": age})
    if index_type is not None:
        table.create_index("age", index_type=index_type)
    return table


def benchmark_query(table: Table, query_age: int, iterations: int) -> float:
    """
    Benchmarks the select query on the given table for a specified number of iterations.

    :param table: The Table instance on which the query is run.
    :param query_age: The age value to use in the equality condition.
    :param iterations: The number of iterations to run the query.
    :return: The average query execution time in seconds.
    """
    start = perf_counter()
    for _ in range(iterations):
        _ = table.select(where=Condition(table.age == query_age))
    end = perf_counter()
    return (end - start) / iterations


def run_benchmarks(
    n: int = 10000,
    iterations: int = 10,
    query_age: int = 30,
    *,
    seed: Optional[int] = 42,
) -> BenchmarkResult:
    """
    Runs benchmarks for three cases:
      1. Without an index.
      2. With a hash index.
      3. With a sorted index.

    It prints the average query time for each case.

    :param n: Number of records to insert into each table.
    :param iterations: Number of iterations to run the query for timing.
    :param query_age: The age value used in the query condition.
    """
    # Deterministic dataset for fair comparison
    if seed is not None:
        random.seed(seed)

    # Without index
    table_no_index = populate_table(n)
    time_no_index = benchmark_query(table_no_index, query_age, iterations)

    # With hash index
    table_hash = populate_table(n, index_type="hash")
    time_hash = benchmark_query(table_hash, query_age, iterations)

    # With sorted index
    table_sorted = populate_table(n, index_type="sorted")
    time_sorted = benchmark_query(table_sorted, query_age, iterations)

    return {
        "without_index": time_no_index,
        "hash_index": time_hash,
        "sorted_index": time_sorted,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Benchmark DictDB select performance")
    parser.add_argument("--rows", type=int, default=10000, help="Number of records")
    parser.add_argument(
        "--iterations", type=int, default=10, help="Iterations per case"
    )
    parser.add_argument("--age", type=int, default=30, help="Age value to query")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for data")
    parser.add_argument(
        "--profile", action="store_true", help="Profile the run with cProfile"
    )
    parser.add_argument(
        "--json-out", type=str, default=None, help="Write results to JSON file"
    )
    args = parser.parse_args()

    # Reduce logging overhead to not skew results
    configure_logging(level="WARNING", console=False, logfile=None)

    def _runner() -> None:
        results = run_benchmarks(
            n=args.rows, iterations=args.iterations, query_age=args.age, seed=args.seed
        )
        # Pretty print
        print(
            f"\nRows={args.rows}, iterations={args.iterations}, query_age={args.age}, seed={args.seed}"
        )
        print(
            "Average query time without index: {:.6f} s".format(
                results["without_index"]
            )
        )
        print(
            "Average query time with hash index: {:.6f} s".format(results["hash_index"])
        )
        print(
            "Average query time with sorted index: {:.6f} s".format(
                results["sorted_index"]
            )
        )
        # Speedups
        if results["without_index"] > 0:
            print(
                "Hash speedup:  x{:.2f}".format(
                    results["without_index"] / results["hash_index"]
                )
            )
            print(
                "Sorted speedup: x{:.2f}".format(
                    results["without_index"] / results["sorted_index"]
                )
            )
        if args.json_out:
            payload = {
                "rows": args.rows,
                "iterations": args.iterations,
                "age": args.age,
                "seed": args.seed,
                "results": results,
            }
            with open(args.json_out, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2)
            print(f"Results written to {args.json_out}")

    if args.profile:
        cProfile.runctx("_runner()", globals(), locals(), sort="cumtime")
    else:
        _runner()
