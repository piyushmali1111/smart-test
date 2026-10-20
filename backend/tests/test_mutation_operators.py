"""Tests verifying that mutation operators produce valid compilable Python syntax."""

import ast
from smarttest.mutation.operators import (
    enumerate_mutants_in_ast,
    SingleMutationTransformer,
)

SAMPLE_SNIPPET = """
def calculate(a, b, flag):
    if a > 10 and not flag:
        x = a + b
        return x
    return 0
"""


def test_mutation_operators_compilation_and_single_change():
    tree = ast.parse(SAMPLE_SNIPPET)
    candidates = enumerate_mutants_in_ast(tree)

    assert len(candidates) >= 4

    for cand in candidates:
        transformer = SingleMutationTransformer(
            target_lineno=cand.lineno,
            target_col=cand.col_offset,
            mutation_type=cand.transformer_type,
            replacement=cand.replacement,
        )

        orig_tree = ast.parse(SAMPLE_SNIPPET)
        mutated_tree = transformer.visit(orig_tree)
        ast.fix_missing_locations(mutated_tree)

        assert transformer.applied is True

        # Unparse and compile must succeed
        code_str = ast.unparse(mutated_tree)
        compiled = compile(code_str, "<mutant_test>", "exec")
        assert compiled is not None
