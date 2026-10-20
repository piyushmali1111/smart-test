"""AST Mutation Operators for creating controlled software bugs."""

import ast
import copy
from typing import List, Dict, Tuple, Any, Optional


class SingleMutationTransformer(ast.NodeTransformer):
    """Applies a single mutation at a specific target (lineno, col_offset, op_type)."""

    def __init__(self, target_lineno: int, target_col: int, mutation_type: str, replacement: Any):
        super().__init__()
        self.target_lineno = target_lineno
        self.target_col = target_col
        self.mutation_type = mutation_type
        self.replacement = replacement
        self.applied = False

    def visit_BinOp(self, node: ast.BinOp) -> ast.AST:
        if (
            not self.applied
            and self.mutation_type == "arithmetic"
            and node.lineno == self.target_lineno
            and node.col_offset == self.target_col
        ):
            self.applied = True
            new_node = copy.deepcopy(node)
            new_node.op = self.replacement()
            return ast.copy_location(new_node, node)
        return self.generic_visit(node)

    def visit_Compare(self, node: ast.Compare) -> ast.AST:
        if (
            not self.applied
            and self.mutation_type == "comparison"
            and node.lineno == self.target_lineno
            and node.col_offset == self.target_col
            and len(node.ops) > 0
        ):
            self.applied = True
            new_node = copy.deepcopy(node)
            new_node.ops[0] = self.replacement()
            return ast.copy_location(new_node, node)
        return self.generic_visit(node)

    def visit_BoolOp(self, node: ast.BoolOp) -> ast.AST:
        if (
            not self.applied
            and self.mutation_type == "boolean_op"
            and node.lineno == self.target_lineno
            and node.col_offset == self.target_col
        ):
            self.applied = True
            new_node = copy.deepcopy(node)
            new_node.op = self.replacement()
            return ast.copy_location(new_node, node)
        return self.generic_visit(node)

    def visit_UnaryOp(self, node: ast.UnaryOp) -> ast.AST:
        if (
            not self.applied
            and self.mutation_type == "remove_not"
            and node.lineno == self.target_lineno
            and node.col_offset == self.target_col
            and isinstance(node.op, ast.Not)
        ):
            self.applied = True
            return ast.copy_location(copy.deepcopy(node.operand), node)
        return self.generic_visit(node)

    def visit_Constant(self, node: ast.Constant) -> ast.AST:
        if (
            not self.applied
            and self.mutation_type == "constant"
            and node.lineno == self.target_lineno
            and node.col_offset == self.target_col
        ):
            self.applied = True
            new_node = copy.deepcopy(node)
            new_node.value = self.replacement
            return ast.copy_location(new_node, node)
        return self.generic_visit(node)

    def visit_Return(self, node: ast.Return) -> ast.AST:
        if (
            not self.applied
            and self.mutation_type == "return_none"
            and node.lineno == self.target_lineno
            and node.col_offset == self.target_col
        ):
            self.applied = True
            new_node = ast.Return(value=ast.Constant(value=None))
            return ast.copy_location(new_node, node)
        return self.generic_visit(node)


class MutantCandidate:
    def __init__(
        self,
        category: str,
        lineno: int,
        col_offset: int,
        orig_repr: str,
        mut_repr: str,
        transformer_type: str,
        replacement: Any,
    ):
        self.category = category
        self.lineno = lineno
        self.col_offset = col_offset
        self.orig_repr = orig_repr
        self.mut_repr = mut_repr
        self.transformer_type = transformer_type
        self.replacement = replacement


def enumerate_mutants_in_ast(tree: ast.AST) -> List[MutantCandidate]:
    """Scans an AST and lists all potential single-mutation candidate sites."""
    candidates: List[MutantCandidate] = []

    arithmetic_map = {
        ast.Add: (ast.Sub, "+", "-"),
        ast.Sub: (ast.Add, "-", "+"),
        ast.Mult: (ast.FloorDiv, "*", "//"),
        ast.FloorDiv: (ast.Mult, "//", "*"),
        ast.Mod: (ast.Mult, "%", "*"),
    }

    comparison_map = {
        ast.Lt: (ast.LtE, "<", "<="),
        ast.Gt: (ast.GtE, ">", ">="),
        ast.LtE: (ast.Lt, "<=", "<"),
        ast.GtE: (ast.Gt, ">=", ">"),
        ast.Eq: (ast.NotEq, "==", "!="),
        ast.NotEq: (ast.Eq, "!=", "=="),
    }

    for node in ast.walk(tree):
        lineno = getattr(node, "lineno", 0)
        col = getattr(node, "col_offset", 0)
        if lineno == 0:
            continue

        # 1. Arithmetic
        if isinstance(node, ast.BinOp):
            op_cls = type(node.op)
            if op_cls in arithmetic_map:
                rep_cls, o_str, m_str = arithmetic_map[op_cls]
                candidates.append(
                    MutantCandidate(
                        category="arithmetic",
                        lineno=lineno,
                        col_offset=col,
                        orig_repr=o_str,
                        mut_repr=m_str,
                        transformer_type="arithmetic",
                        replacement=rep_cls,
                    )
                )

        # 2. Comparison
        elif isinstance(node, ast.Compare) and len(node.ops) > 0:
            cmp_cls = type(node.ops[0])
            if cmp_cls in comparison_map:
                rep_cls, o_str, m_str = comparison_map[cmp_cls]
                candidates.append(
                    MutantCandidate(
                        category="comparison",
                        lineno=lineno,
                        col_offset=col,
                        orig_repr=o_str,
                        mut_repr=m_str,
                        transformer_type="comparison",
                        replacement=rep_cls,
                    )
                )

        # 3. Boolean
        elif isinstance(node, ast.BoolOp):
            if isinstance(node.op, ast.And):
                candidates.append(
                    MutantCandidate(
                        category="boolean",
                        lineno=lineno,
                        col_offset=col,
                        orig_repr="and",
                        mut_repr="or",
                        transformer_type="boolean_op",
                        replacement=ast.Or,
                    )
                )
            elif isinstance(node.op, ast.Or):
                candidates.append(
                    MutantCandidate(
                        category="boolean",
                        lineno=lineno,
                        col_offset=col,
                        orig_repr="or",
                        mut_repr="and",
                        transformer_type="boolean_op",
                        replacement=ast.And,
                    )
                )

        # 4. Remove Not
        elif isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
            candidates.append(
                MutantCandidate(
                    category="boolean",
                    lineno=lineno,
                    col_offset=col,
                    orig_repr="not",
                    mut_repr="(removed not)",
                    transformer_type="remove_not",
                    replacement=None,
                )
            )

        # 5. Constants
        elif isinstance(node, ast.Constant):
            val = node.value
            if isinstance(val, bool):
                candidates.append(
                    MutantCandidate(
                        category="constant",
                        lineno=lineno,
                        col_offset=col,
                        orig_repr=str(val),
                        mut_repr=str(not val),
                        transformer_type="constant",
                        replacement=not val,
                    )
                )
            elif isinstance(val, (int, float)) and not isinstance(val, bool):
                if val == 0:
                    candidates.append(
                        MutantCandidate(
                            category="constant",
                            lineno=lineno,
                            col_offset=col,
                            orig_repr="0",
                            mut_repr="1",
                            transformer_type="constant",
                            replacement=1,
                        )
                    )
                elif val == 1:
                    candidates.append(
                        MutantCandidate(
                            category="constant",
                            lineno=lineno,
                            col_offset=col,
                            orig_repr="1",
                            mut_repr="0",
                            transformer_type="constant",
                            replacement=0,
                        )
                    )

        # 6. Return None
        elif isinstance(node, ast.Return) and node.value is not None:
            candidates.append(
                MutantCandidate(
                    category="statement",
                    lineno=lineno,
                    col_offset=col,
                    orig_repr="return expr",
                    mut_repr="return None",
                    transformer_type="return_none",
                    replacement=None,
                )
            )

    return candidates
