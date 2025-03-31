#!/usr/bin/env python
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
    $ python scripts/benchmark.py

Author: Your Name
Date: YYYY-MM-DD
"""

import cProfile
import random
from time import perf_counter
from typing import TypedDict

from dictdb import Table, Query


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


def populate_table(n: int, index_type: str = None) -> Table:
    """
    Populates a new DictDB Table with n records.

    Each record has an 'id', 'name', and 'age'. If index_type is provided,
    an index on the 'age' field is created with the specified type ("hash" or "sorted").

    :param n: Number of records to insert.
    :param index_type: Type of index to create ("hash" or "sorted"), or None.
    :return: A populated Table instance.
    """
    table = Table("benchmark_table", primary_key="id", schema={"id": int, "name": str, "age": int})
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
        _ = table.select(where=Query(table.age == query_age))
    end = perf_counter()
    return (end - start) / iterations


def run_benchmarks(n: int = 10000, iterations: int = 10, query_age: int = 30) -> None:
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
    # Without index
    table_no_index = populate_table(n)
    time_no_index = benchmark_query(table_no_index, query_age, iterations)

    # With hash index
    table_hash = populate_table(n, index_type="hash")
    time_hash = benchmark_query(table_hash, query_age, iterations)

    # With sorted index
    table_sorted = populate_table(n, index_type="sorted")
    time_sorted = benchmark_query(table_sorted, query_age, iterations)

    print(f"\nPopulating table with {n} records and benchmarking queries over {iterations} iterations...")
    print("Average query time without index: {:.6f} seconds".format(time_no_index))
    print("Average query time with hash index: {:.6f} seconds".format(time_hash))
    print("Average query time with sorted index: {:.6f} seconds\n".format(time_sorted))


if __name__ == "__main__":
    # Run the benchmark with cProfile and sort the output by cumulative time.
    cProfile.run("run_benchmarks(n=10000, iterations=10, query_age=30)", sort="cumtime")
