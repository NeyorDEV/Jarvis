import os
import sys

def main():
    dir_old = r"n:\JARVIS"
    dir_new = r"N:\JARVIS8.5"

    print(f"Comparing {dir_old} vs {dir_new}...\n")

    # 1. Gather all python files in both directories
    def get_py_files(base_dir):
        files_dict = {}
        for root, dirs, files in os.walk(base_dir):
            if "venv" in root or "__pycache__" in root or ".git" in root or ".claude" in root or ".agents" in root:
                continue
            for f in files:
                if f.endswith(".py"):
                    full_path = os.path.join(root, f)
                    rel_path = os.path.relpath(full_path, base_dir)
                    files_dict[rel_path] = full_path
        return files_dict

    old_files = get_py_files(dir_old)
    new_files = get_py_files(dir_new)

    print(f"Old py files: {len(old_files)}")
    print(f"New py files: {len(new_files)}\n")

    # 2. Check for new files in 8.5
    # Since 8.5 has flattened structures, we should compare by filename rather than relative path
    old_by_name = {os.path.basename(p): p for p in old_files.values()}
    new_by_name = {os.path.basename(p): p for p in new_files.values()}

    added = []
    removed = []
    modified = []

    for name, path_new in new_by_name.items():
        if name not in old_by_name:
            added.append(name)
        else:
            # Compare sizes or contents
            with open(old_by_name[name], "r", encoding="utf-8", errors="ignore") as f1:
                content_old = f1.read()
            with open(path_new, "r", encoding="utf-8", errors="ignore") as f2:
                content_new = f2.read()
            if content_old != content_new:
                modified.append((name, len(content_old), len(content_new), old_by_name[name], path_new))

    for name in old_by_name:
        if name not in new_by_name:
            removed.append(name)

    print("=== ADDED FILES ===")
    for a in sorted(added):
        print(f"[NEW] {a}")
    print()

    print("=== REMOVED FILES ===")
    for r in sorted(removed):
        print(f"[DEL] {r}")
    print()

    print("=== MODIFIED FILES ===")
    for m, sz_old, sz_new, p_old, p_new in sorted(modified):
        print(f"[MOD] {m} (Size: {sz_old} -> {sz_new} bytes)")
    print()

if __name__ == "__main__":
    main()
