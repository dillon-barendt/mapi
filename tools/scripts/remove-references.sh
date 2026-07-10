search() {
  if command -v rg >/dev/null 2>&1; then
    rg -n --hidden --glob '!.git' --glob '!.venv' "$@"
  else
    grep -RIn --exclude-dir=".git" --exclude-dir=".venv" "$@" .
  fi
}
# usage:
search 'ticketvision_core'
