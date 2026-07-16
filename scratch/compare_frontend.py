import os
import sys

def main():
    dir_old = r"n:\JARVIS\frontend"
    dir_new = r"N:\JARVIS8.5\frontend"

    print(f"Comparing frontend {dir_old} vs {dir_new}...\n")

    def get_frontend_files(base_dir):
        files_dict = {}
        for root, dirs, files in os.walk(base_dir):
            if "node_modules" in root or "dist" in root or ".git" in root:
                continue
            for f in files:
                if f.endswith((".ts", ".js", ".html", ".css")):
                    full_path = os.path.join(root, f)
                    rel_path = os.path.relpath(full_path, base_dir)
                    files_dict[rel_path] = full_path
        return files_dict

    old_files = get_frontend_files(dir_old)
    new_files = get_frontend_files(dir_new)

    added = []
    removed = []
    modified = []

    for rel_path, path_new in new_files.items():
        if rel_path not in old_files:
            added.append(rel_path)
        else:
            with open(old_files[rel_path], "r", encoding="utf-8", errors="ignore") as f1:
                content_old = f1.read()
            with open(path_new, "r", encoding="utf-8", errors="ignore") as f2:
                content_new = f2.read()
            if content_old != content_new:
                modified.append((rel_path, len(content_old), len(content_new)))

    for rel_path in old_files:
        if rel_path not in new_files:
            removed.append(rel_path)

    print("=== ADDED FILES ===")
    for a in sorted(added):
        print(f"[NEW] {a}")
    print()

    print("=== REMOVED FILES ===")
    for r in sorted(removed):
        print(f"[DEL] {r}")
    print()

    print("=== MODIFIED FILES ===")
    for m, sz_old, sz_new in sorted(modified):
        print(f"[MOD] {m} (Size: {sz_old} -> {sz_new} bytes)")
    print()

if __name__ == "__main__":
    main()
