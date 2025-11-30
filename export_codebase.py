import os

# Project root (change if needed)
PROJECT_ROOT = "."

# Output file
OUTPUT_FILE = "codebase.md"

# Extensions to include
INCLUDE_EXTS = (".py", ".html", ".css", ".js", ".tsx", ".ts", ".json", ".yml", ".yaml", ".md", ".txt")

with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
    out.write("# MoneySplit Project Codebase\n\n")
    out.write("Complete source code export for Assignment 2\n\n")
    out.write("---\n\n")

    for root, dirs, files in os.walk(PROJECT_ROOT):
        # Skip virtual envs or hidden folders
        if any(skip in root for skip in [".git", "__pycache__", ".venv", "node_modules", "htmlcov", ".pytest_cache", "build", "dist"]):
            continue

        # Write folder name
        rel_path = os.path.relpath(root, PROJECT_ROOT)
        if rel_path == ".":
            rel_path = "Root"
        out.write(f"\n\n## 📂 {rel_path}\n\n")

        for file in sorted(files):
            if file.endswith(INCLUDE_EXTS):
                filepath = os.path.join(root, file)
                out.write(f"\n### 📄 {file}\n\n")

                # Determine syntax highlighting
                ext = filepath.split(".")[-1]
                syntax_map = {
                    "py": "python",
                    "js": "javascript",
                    "jsx": "javascript",
                    "ts": "typescript",
                    "tsx": "typescript",
                    "html": "html",
                    "css": "css",
                    "json": "json",
                    "yml": "yaml",
                    "yaml": "yaml",
                    "md": "markdown",
                    "txt": "text"
                }
                syntax = syntax_map.get(ext, "")

                out.write(f"```{syntax}\n")
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        out.write(f.read())
                except Exception as e:
                    out.write(f"⚠️ Could not read file: {e}")
                out.write("\n```\n\n")

print(f"✅ Codebase exported to {OUTPUT_FILE}")
print("📄 To convert to PDF, run one of:")
print("   Option 1: md-to-pdf codebase.md")
print("   Option 2: pandoc codebase.md -o codebase.pdf")
