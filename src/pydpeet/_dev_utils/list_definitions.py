"""Utility to list all functions and classes in the pydpeet project."""

import ast
import os
from pathlib import Path

import pandas as pd


def get_python_files(src_dir: Path, exclude_dirs: list[str] = None) -> list[Path]:
    """Get all Python files in the source directory recursively.

    Args:
        src_dir: Source directory to scan.
        exclude_dirs: List of directory names to exclude.
    """
    if exclude_dirs is None:
        exclude_dirs = []

    python_files = []
    for root, dirs, files in os.walk(src_dir):
        # Skip __pycache__, hidden directories, and excluded directories
        dirs[:] = [d for d in dirs if not d.startswith(".") and d != "__pycache__" and d not in exclude_dirs]

        for file in files:
            if file.endswith(".py"):
                python_files.append(Path(root) / file)
    return python_files


def extract_definitions(file_path: Path) -> tuple[list[dict], list[dict]]:
    """Extract function and class definitions from a Python file."""
    functions = []
    classes = []

    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        tree = ast.parse(content, filename=str(file_path))

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Get function info
                args = [arg.arg for arg in node.args.args]
                functions.append(
                    {
                        "name": node.name,
                        "line": node.lineno,
                        "args": args,
                        "docstring": ast.get_docstring(node),
                    }
                )
            elif isinstance(node, ast.ClassDef):
                # Get class methods
                methods = []
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        methods.append(item.name)

                classes.append(
                    {
                        "name": node.name,
                        "line": node.lineno,
                        "methods": methods,
                        "docstring": ast.get_docstring(node),
                    }
                )
    except (SyntaxError, UnicodeDecodeError) as e:
        print(f"Warning: Could not parse {file_path}: {e}")

    return functions, classes


def list_all_definitions(src_dir: Path = None, exclude_dirs: list[str] = None) -> dict[str, dict]:
    """
    List all functions and classes in the pydpeet project.

    Args:
        src_dir: Path to the source directory. Defaults to pydpeet/src.
        exclude_dirs: List of directory names to exclude.

    Returns:
        Dictionary mapping file paths to their functions and classes.
    """
    if src_dir is None:
        # Default to pydpeet/src directory
        # Script is at: pydpeet/src/pydpeet/_dev_utils/list_definitions.py
        # We need to go up 3 levels to reach pydpeet/src
        src_dir = Path(__file__).parent.parent.parent

    if exclude_dirs is None:
        exclude_dirs = ["_dev_utils", "citations", "res"]  # Default exclude _dev_utils, citations, and res

    if not src_dir.exists():
        raise FileNotFoundError(f"Source directory not found: {src_dir}")

    python_files = get_python_files(src_dir, exclude_dirs)
    results = {}

    for file_path in python_files:
        # Get relative path from src_dir
        rel_path = file_path.relative_to(src_dir)
        functions, classes = extract_definitions(file_path)

        if functions or classes:
            results[str(rel_path)] = {
                "functions": functions,
                "classes": classes,
            }

    return results


def print_definitions(results: dict[str, dict], show_docstrings: bool = False) -> None:
    """
    Print all functions and classes in a pandas DataFrame.

    Args:
        results: Dictionary from list_all_definitions.
        show_docstrings: Whether to include docstrings in the output.
    """
    # Collect all items into a list for DataFrame
    items = []

    for file_path, data in results.items():
        functions = data["functions"]
        classes = data["classes"]

        # Add standalone functions
        for func in functions:
            category = "PRIVATE" if func["name"].startswith("_") else "OPEN"

            items.append(
                {
                    "Category": category,
                    "Name": func["name"],
                    "File": file_path,
                    "Line": func["line"],
                }
            )

        # Add classes
        for cls in classes:
            category = "PRIVATE" if cls["name"].startswith("_") else "OPEN"

            # Add the class itself
            items.append(
                {
                    "Category": category,
                    "Name": cls["name"],
                    "File": file_path,
                    "Line": cls["line"],
                }
            )

            # Add class methods
            for method_name in cls["methods"]:
                method_category = "PRIVATE" if method_name.startswith("_") else "OPEN"
                items.append(
                    {
                        "Category": method_category,
                        "Name": f"{cls['name']}.{method_name}",
                        "File": file_path,
                        "Line": cls["line"],  # Class line number (method lines not tracked)
                    }
                )

    # Create DataFrame
    df = pd.DataFrame(items)

    if df.empty:
        print("No functions or classes found.")
        return

    # Sort by Category, File, Line
    df = df.sort_values(["Category", "File", "Line"]).reset_index(drop=True)

    # Configure pandas to display all rows and columns
    pd.set_option("display.max_rows", None)
    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", None)
    pd.set_option("display.max_colwidth", None)

    # Print the DataFrame
    print(df)

    # Print summary
    print(f"\n{'=' * 80}")
    print("Summary:")
    print(f"  [OPEN] {len(df[df['Category'] == 'OPEN'])} items")
    print(f"  [PRIVATE] {len(df[df['Category'] == 'PRIVATE'])} items")
    print(f"  Total: {len(df)} items across {len(results)} files")
    print("=" * 80)


def main():
    """Main entry point for the utility."""
    import argparse

    parser = argparse.ArgumentParser(description="List all functions and classes in the pydpeet project")
    parser.add_argument("--src-dir", type=Path, help="Path to the source directory (default: pydpeet/src)")
    parser.add_argument(
        "--exclude",
        nargs="*",
        default=["_dev_utils", "citations", "res"],
        help="List of directory names to exclude (default: _dev_utils, citations, res)",
    )
    parser.add_argument("--docstrings", action="store_true", help="Include docstrings in the output")

    args = parser.parse_args()

    results = list_all_definitions(args.src_dir, args.exclude)
    print_definitions(results, show_docstrings=args.docstrings)


if __name__ == "__main__":
    main()
    print()
