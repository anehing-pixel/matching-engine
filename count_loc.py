import re, sys, os

SRC = r"C:\Users\Administrator\WorkBuddy\2026-10-23-22-56-40\atching-engine\src".replace("atching", "matching")

def strip_block_comments(text):
    # Rust block comments (non-nested assumption is fine for LOC)
    return re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)

def strip_line_comment_and_count(line, in_str):
    # walk chars, track simple " strings, cut at // outside string
    out = []
    i = 0
    n = len(line)
    while i < n:
        c = line[i]
        if c == '"':
            # toggle string state (ignore escaped)
            if not in_str:
                in_str = True
                out.append(c)
            else:
                # check escaped
                if i > 0 and line[i-1] == '\\':
                    out.append(c)
                else:
                    in_str = False
                    out.append(c)
            i += 1
            continue
        if c == '\\' and in_str:
            out.append(c)
            if i+1 < n:
                out.append(line[i+1])
                i += 2
                continue
        if c == '/' and i+1 < n and line[i+1] == '/' and not in_str:
            break  # rest of line is comment
        out.append(c)
        i += 1
    return "".join(out), in_str

def count_file(path):
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        text = f.read()
    text = strip_block_comments(text)
    lines = text.split("\n")

    physical = 0
    code = 0
    depth = 0
    in_test = False
    test_base = 0
    pending_test = False
    in_str = False

    for raw in lines:
        physical += 1
        # strip comments (also handles /// and //!)
        stripped, in_str = strip_line_comment_and_count(raw, in_str)
        s = stripped.strip()
        if s == "":
            continue
        # detect #[cfg(test)] then mod ... {
        if re.search(r"#\[\s*cfg\s*\(\s*test\s*\)\s*\]", s):
            pending_test = True
        m = re.match(r"mod\s+(\w+)\s*\{", s)
        if pending_test and m:
            in_test = True
            pending_test = False
            # count braces on this line to set base depth after opening {
        # brace tracking on the comment-stripped line
        open_b = s.count("{")
        close_b = s.count("}")
        # adjust depth
        if in_test:
            depth += open_b - close_b
            if depth < test_base:
                in_test = False
                test_base = 0
            continue  # skip test content lines
        else:
            if pending_test:
                # we opened test mod this same line; set base after counting
                depth += open_b - close_b
                test_base = depth
                in_test = True
                continue
            depth += open_b - close_b
            code += 1
    return physical, code

all_files = []
for root, dirs, files in os.walk(SRC):
    for fn in files:
        if fn.endswith(".rs"):
            all_files.append(os.path.join(root, fn))

all_files.sort()
total_phys = 0
total_code = 0
lib_phys = 0
lib_code = 0

print(f"{'file':45} {'phys':>6} {'code':>6}")
print("-" * 62)
for p in all_files:
    phys, code = count_file(p)
    rel = os.path.relpath(p, SRC)
    is_bin = "bin" in rel.split(os.sep)
    total_phys += phys
    total_code += code
    if not is_bin:
        lib_phys += phys
        lib_code += code
    print(f"{rel:45} {phys:>6} {code:>6}")

print("-" * 62)
print(f"{'LIBRARY (exclude bin/):':45} {lib_phys:>6} {lib_code:>6}")
print(f"{'ALL (incl bin/):':45} {total_phys:>6} {total_code:>6}")
