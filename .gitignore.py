# # Byte-compiled / optimized / DLL files
# __pycache__/
# *.py[cod]
# *$py.class
#
# # Virtual environment
# .env/
# venv/
#
# # Environment variables
# .env
#
# # Logs and databases
# *.log
# *.sqlite3
#
# # IDE-specific files
# .idea/
# .vscode/
# *.iml
#
# # GitHub settings
# *.DS_Store
#
# # Test coverage reports
# .coverage
# coverage/
# *.cover
# *.py,cover
#
# # Build artifacts
# build/
# dist/
# *.egg-info/
# Byte-compiled / optimized / DLL files
pycache_patterns = ["__pycache__/", "*.py[cod]", "*$py.class"]

# Virtual environment
virtual_env_patterns = [".env/", "venv/"]

# Environment variables
env_file_patterns = [".env"]

# Logs and databases
log_and_db_patterns = ["*.log", "*.sqlite3"]

# IDE-specific files
ide_specific_patterns = [".idea/", ".vscode/", "*.iml"]

# GitHub settings
github_settings_patterns = ["*.DS_Store"]

# Test coverage reports
test_coverage_patterns = [".coverage", "coverage/", "*.cover", "*.py,cover"]

# Build artifacts
build_artifact_patterns = ["build/", "dist/", "*.egg-info/"]
