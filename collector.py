import os
import argparse
from pathlib import Path
import pathspec

def load_all_gitignore_specs(root_dir):
    """Recursively collects all .gitignore specs from the root directory."""
    ignore_specs = {}

    for dirpath, _, filenames in os.walk(root_dir):
        ignore_file = os.path.join(dirpath, '.gitignore')
        if '.gitignore' in filenames:
            with open(ignore_file, 'r', encoding='utf-8') as f:
                lines = f.read().splitlines()
            patterns = [line for line in lines if line and not line.startswith('#')]
            ignore_specs[os.path.normpath(dirpath)] = pathspec.PathSpec.from_lines('gitwildmatch', patterns)

    return ignore_specs

def is_ignored(path, ignore_specs, root_dir):
    """Check if the path is ignored based on .gitignore patterns found in parent directories."""
    rel_path = os.path.relpath(path, root_dir)
    norm_path = os.path.normpath(path)

    for dir_path, spec in ignore_specs.items():
        # Check if path is under this .gitignore directory
        if os.path.commonpath([norm_path, dir_path]) == dir_path:
            relative = os.path.relpath(path, dir_path).replace(os.sep, '/')
            if spec.match_file(relative):
                return True
    return False

def generate_tree_structure(root_dir, ignore_specs, exclude_dirs):
    """Generate a textual tree representation of the directory structure."""
    tree_lines = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        dirpath = os.path.normpath(dirpath)

        # Skip this directory if it's ignored or explicitly excluded
        if is_ignored(dirpath, ignore_specs, root_dir) or dirpath in exclude_dirs:
            dirnames[:] = []
            continue

        depth = dirpath.replace(root_dir, '').count(os.sep)
        indent = ' ' * 4 * depth
        tree_lines.append(f"{indent}{os.path.basename(dirpath)}/")

        subindent = ' ' * 4 * (depth + 1)

        # Filter subdirectories: skip hidden, ignored, or excluded
        dirnames[:] = [
            d for d in dirnames
            if not d.startswith('.') and
            not is_ignored(os.path.join(dirpath, d), ignore_specs, root_dir) and
            os.path.normpath(os.path.join(dirpath, d)) not in exclude_dirs
        ]

        for fname in filenames:
            fpath = os.path.join(dirpath, fname)
            if not is_ignored(fpath, ignore_specs, root_dir):
                tree_lines.append(f"{subindent}{fname}")

    return '\n'.join(tree_lines)


def collect_codebase(root_dir, output_file, include_exts=None, exclude_dirs=None, exclude_files=None):
    if exclude_dirs is None:
        exclude_dirs = []
    if exclude_files is None:
        exclude_files = []

    exclude_dirs = [os.path.abspath(os.path.normpath(os.path.join(root_dir, d))) for d in exclude_dirs]
    exclude_files = {os.path.normpath(os.path.join(root_dir, f)) for f in exclude_files}

    root_dir = os.path.abspath(root_dir)
    ignore_specs = load_all_gitignore_specs(root_dir)

    output_dir = os.path.join(os.path.dirname(output_file), "codebases")
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, os.path.basename(output_file))

    with open(output_file, 'w', encoding='utf-8') as out:
        tree_structure = generate_tree_structure(root_dir, ignore_specs, exclude_dirs)
        out.write(f"# {root_dir_name}\n\n```\n{tree_structure}\n```\n\n")

        for dirpath, dirnames, filenames in os.walk(root_dir):
            dirpath = os.path.normpath(dirpath)

            # Skip directory if it's ignored or explicitly excluded
            if is_ignored(dirpath, ignore_specs, root_dir) or dirpath in exclude_dirs:
                dirnames[:] = []
                continue

            # Filter subdirectories to exclude ignored and explicitly excluded
            dirnames[:] = [
                d for d in dirnames
                if not d.startswith('.') and
                not is_ignored(os.path.join(dirpath, d), ignore_specs, root_dir) and
                os.path.normpath(os.path.join(dirpath, d)) not in exclude_dirs
            ]

            dirnames[:] = [d for d in dirnames if not d.startswith('.') and not is_ignored(os.path.join(dirpath, d), ignore_specs, root_dir)]

            for fname in filenames:
                file_path = os.path.normpath(os.path.join(dirpath, fname))
                if (
                    file_path in exclude_files or
                    is_ignored(file_path, ignore_specs, root_dir) or
                    (include_exts and not any(fname.endswith(ext) for ext in include_exts))
                ):
                    continue

                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        code = f.read()
                except Exception:
                    continue

                code = '\n'.join(line.rstrip() for line in code.splitlines() if line.strip())
                if not code:
                    continue

                rel_path = os.path.relpath(file_path, root_dir).replace(os.sep, '/')
                lang = os.path.splitext(fname)[1].lstrip('.')
                out.write(f"// {rel_path}\n{code}\n\n")

def parse_args():
    a = argparse.ArgumentParser()
    a.add_argument("root", help="Root directory of the codebase to collect.")
    a.add_argument("out", nargs='?', default=None, help="Output file for the collected code snippets.")
    a.add_argument("--ext", nargs='*', default=None, help="Include only files with these extensions.")
    a.add_argument("--exclude", nargs='*', default=None, help="Exclude these directories from processing.")
    a.add_argument("--exclude_files", nargs='*', default=None, help="Exclude these specific files from processing.")
    return a.parse_args()

if __name__ == "__main__":
    args = parse_args()

    if args.out is None:
        root_dir_name = os.path.basename(os.path.normpath(args.root))
        args.out = f"{root_dir_name}.md"

    collect_codebase(args.root, args.out, args.ext, args.exclude, args.exclude_files)
