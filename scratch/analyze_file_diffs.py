import os
import sys
import difflib

def diff_files(old_path, new_path):
    with open(old_path, 'r', encoding='utf-8', errors='ignore') as f:
        old_lines = f.readlines()
    with open(new_path, 'r', encoding='utf-8', errors='ignore') as f:
        new_lines = f.readlines()
        
    def parse_defs(lines):
        defs = {}
        current_def = None
        current_lines = []
        for line in lines:
            if line.strip().startswith(('def ', 'class ')):
                if current_def:
                    defs[current_def] = current_lines
                m = line.strip().split()
                if len(m) > 1:
                    name = m[1].split('(')[0].split(':')[0]
                    current_def = name
                    current_lines = [line]
            elif current_def:
                current_lines.append(line)
        if current_def:
            defs[current_def] = current_lines
        return defs

    old_defs = parse_defs(old_lines)
    new_defs = parse_defs(new_lines)
    
    added_defs = []
    removed_defs = []
    modified_defs = []
    
    for name in new_defs:
        if name not in old_defs:
            added_defs.append(name)
        else:
            old_body = "".join(old_defs[name])
            new_body = "".join(new_defs[name])
            if old_body != new_body:
                modified_defs.append(name)
                
    for name in old_defs:
        if name not in new_defs:
            removed_defs.append(name)
            
    return {
        "added": added_defs,
        "removed": removed_defs,
        "modified": modified_defs,
        "old_line_count": len(old_lines),
        "new_line_count": len(new_lines)
    }

def main():
    sys.stdout.reconfigure(errors="replace")
    
    dir_old = r"n:\JARVIS"
    dir_new = r"N:\JARVIS8.5"
    
    def find_all_py_files(base_dir):
        files_dict = {}
        for root, dirs, files in os.walk(base_dir):
            if "venv" in root or "__pycache__" in root or ".git" in root:
                continue
            for f in files:
                if f.endswith(".py"):
                    files_dict[f] = os.path.join(root, f)
        return files_dict

    old_py_files = find_all_py_files(dir_old)
    new_py_files = find_all_py_files(dir_new)
    
    # Analyze only the first half of modified files to avoid truncation
    modified_files = [
        "app_launcher.py", "deezer_controller.py",
        "file_manager.py", "google_services.py", "ha_config.py", "main2.py"
    ]
    
    for filename in modified_files:
        if filename not in old_py_files or filename not in new_py_files:
            continue
            
        old_path = old_py_files[filename]
        new_path = new_py_files[filename]
        
        print(f"==================================================")
        print(f"FILE: {filename}")
        print(f"==================================================")
        
        diff = diff_files(old_path, new_path)
        print(f"  Lines: {diff['old_line_count']} -> {diff['new_line_count']}")
        print(f"  Added functions/classes: {diff['added']}")
        print(f"  Removed functions/classes: {diff['removed']}")
        print(f"  Modified functions/classes: {diff['modified']}")
        
        if diff['modified'] or diff['removed'] or diff['added']:
            print("  --- Structural Changes / Diff Sample ---")
            with open(old_path, 'r', encoding='utf-8', errors='ignore') as f:
                old_lines = f.readlines()
            with open(new_path, 'r', encoding='utf-8', errors='ignore') as f:
                new_lines = f.readlines()
                
            old_defs = {}
            new_defs = {}
            
            def get_defs_with_body(lines):
                defs = {}
                current_def = None
                current_lines = []
                for line in lines:
                    if line.strip().startswith(('def ', 'class ')):
                        if current_def:
                            defs[current_def] = current_lines
                        m = line.strip().split()
                        if len(m) > 1:
                            name = m[1].split('(')[0].split(':')[0]
                            current_def = name
                            current_lines = [line]
                    elif current_def:
                        current_lines.append(line)
                if current_def:
                    defs[current_def] = current_lines
                return defs
                
            old_defs = get_defs_with_body(old_lines)
            new_defs = get_defs_with_body(new_lines)
            
            # Print sample for some modified defs
            for m_def in diff['modified'][:4]:
                if m_def in old_defs and m_def in new_defs:
                    old_body = old_defs[m_def]
                    new_body = new_defs[m_def]
                    diff_res = list(difflib.unified_diff(old_body, new_body, fromfile='old', tofile='new', n=1))
                    additions = [line.strip() for line in diff_res if line.startswith('+') and not line.startswith('+++')]
                    deletions = [line.strip() for line in diff_res if line.startswith('-') and not line.startswith('---')]
                    print(f"    Modified '{m_def}': +{len(additions)} lines, -{len(deletions)} lines")
                    if additions:
                        print(f"      + Added sample: {additions[:3]}")
                    if deletions:
                        print(f"      - Removed sample: {deletions[:3]}")
        print()

if __name__ == "__main__":
    main()
