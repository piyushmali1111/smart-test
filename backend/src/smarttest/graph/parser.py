"""Static AST Code Parser to extract functions and static call graphs."""

import ast
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional, Any


class FunctionInfo:
    def __init__(
        self,
        func_id: str,
        label: str,
        module: str,
        file_path: str,
        start_line: int,
        end_line: int,
        kind: str = "function",
    ):
        self.func_id = func_id
        self.label = label
        self.module = module
        self.file_path = file_path
        self.start_line = start_line
        self.end_line = end_line
        self.kind = kind

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.func_id,
            "label": self.label,
            "file": self.file_path,
            "kind": self.kind,
            "startLine": self.start_line,
            "endLine": self.end_line,
        }


class CallGraphParser:
    """Parses Python source files using AST to extract functions and call edges."""

    def __init__(self, root_dir: Path):
        self.root_dir = root_dir
        self.functions: Dict[str, FunctionInfo] = {}
        self.edges: Set[Tuple[str, str]] = set()
        self.unresolved_calls: int = 0
        self.resolved_calls: int = 0

    def parse_codebase(self) -> Tuple[Dict[str, FunctionInfo], List[Tuple[str, str]], int]:
        """Scans all Python files in root_dir, extracting functions and call dependencies."""
        py_files = sorted(list(self.root_dir.glob("**/*.py")))
        ast_trees: Dict[str, Tuple[Path, ast.AST, str]] = {}

        # 1. First pass: extract all function definitions and line numbers
        for py_path in py_files:
            rel_file = str(py_path.relative_to(self.root_dir.parent)).replace("\\", "/")
            module_name = py_path.stem
            if module_name == "__init__":
                module_name = py_path.parent.name

            try:
                with open(py_path, "r", encoding="utf-8") as f:
                    content = f.read()
                tree = ast.parse(content, filename=str(py_path))
                ast_trees[module_name] = (py_path, tree, rel_file)
            except Exception:
                continue

            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    func_id = f"{module_name}.{node.name}"
                    self.functions[func_id] = FunctionInfo(
                        func_id=func_id,
                        label=node.name,
                        module=module_name,
                        file_path=rel_file,
                        start_line=node.lineno,
                        end_line=getattr(node, "end_lineno", node.lineno + 10),
                        kind="function",
                    )

        # 2. Second pass: extract call edges A -> B (A uses B)
        for module_name, (py_path, tree, rel_file) in ast_trees.items():
            self._extract_calls(module_name, tree)

        edge_list = sorted(list(self.edges))
        return self.functions, edge_list, self.unresolved_calls

    def _extract_calls(self, module_name: str, tree: ast.AST) -> None:
        """Inspects module AST to map imports and identify function-to-function calls."""
        # Map imported identifiers: name -> target_func_id or module_alias -> target_module
        imports: Dict[str, str] = {}
        module_aliases: Dict[str, str] = {}

        for node in tree.body:
            if isinstance(node, ast.Import):
                for alias in node.names:
                    pkg_mod = alias.name.split(".")[-1]
                    alias_name = alias.asname or pkg_mod
                    module_aliases[alias_name] = pkg_mod
            elif isinstance(node, ast.ImportFrom):
                src_mod = (node.module or "").split(".")[-1]
                for alias in node.names:
                    alias_name = alias.asname or alias.name
                    target_func = f"{src_mod}.{alias.name}"
                    imports[alias_name] = target_func

        # Visit each function in the module
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                caller_id = f"{module_name}.{node.name}"
                self._inspect_function_calls(caller_id, module_name, node, imports, module_aliases)

    def _inspect_function_calls(
        self,
        caller_id: str,
        module_name: str,
        func_node: ast.AST,
        imports: Dict[str, str],
        module_aliases: Dict[str, str],
    ) -> None:
        """Walks AST of a single function to detect calls and resolve their target."""
        for subnode in ast.walk(func_node):
            # Check local imports inside function (e.g. for circular imports)
            if isinstance(subnode, ast.ImportFrom):
                src_mod = (subnode.module or "").split(".")[-1]
                for alias in subnode.names:
                    alias_name = alias.asname or alias.name
                    imports[alias_name] = f"{src_mod}.{alias.name}"
            elif isinstance(subnode, ast.Import):
                for alias in subnode.names:
                    pkg_mod = alias.name.split(".")[-1]
                    module_aliases[alias.asname or pkg_mod] = pkg_mod

            if isinstance(subnode, ast.Call):
                resolved_id = self._resolve_call(subnode.func, module_name, imports, module_aliases)
                if resolved_id and resolved_id in self.functions and resolved_id != caller_id:
                    self.edges.add((caller_id, resolved_id))
                    self.resolved_calls += 1
                else:
                    self.unresolved_calls += 1

    def _resolve_call(
        self,
        call_func: ast.AST,
        current_module: str,
        imports: Dict[str, str],
        module_aliases: Dict[str, str],
    ) -> Optional[str]:
        """Resolves an ast.Call.func node into a fully-qualified function ID."""
        # 1. Simple function call: func_name(...)
        if isinstance(call_func, ast.Name):
            name = call_func.id
            if name in imports:
                return imports[name]
            # Same module call
            same_mod = f"{current_module}.{name}"
            if same_mod in self.functions:
                return same_mod
            return None

        # 2. Attribute call: mod.func_name(...) or obj.method(...)
        if isinstance(call_func, ast.Attribute):
            attr_name = call_func.attr
            if isinstance(call_func.value, ast.Name):
                obj_name = call_func.value.id
                target_mod = module_aliases.get(obj_name, obj_name)
                candidate_id = f"{target_mod}.{attr_name}"
                if candidate_id in self.functions:
                    return candidate_id
            return None

        return None
