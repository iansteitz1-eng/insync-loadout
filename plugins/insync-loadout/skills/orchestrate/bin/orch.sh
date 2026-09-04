#!/usr/bin/env bash
# orch.sh — hybrid orchestrator harness (2026-06-02).
#
# Drives long-lived LANE TERMINALS over the disk via tmux (the thing the StayCool
# Orchestrator outline was reaching for) AND unifies them with SPAWNED subagents
# through one shared status bus, so `status` shows both kinds of lane the same way.
#
#   tmux lane:     a `claude` (or any cmd) running inside tmux session orch-<lane>.
#                  This terminal dispatches with `send` and glances with `read`.
#   spawned lane:  a subagent/workflow this CC session owns; it (or the orchestrator)
#                  calls `orch.sh report <lane> "..."` to publish state to the bus.
#
# Control channel = tmux send-keys (dispatch). State channel = lanes/<lane>/STATUS.md
# (clean, file-based) — NOT capture-pane scraping of a TUI (noisy). See premortem.
#
# SAFETY: `send` refuses obviously destructive lines unless --force; only touches
# orch-prefixed sessions; never the existing aria-runner session.
set -uo pipefail

ORCH_HOME="${ORCH_HOME:-$HOME/dev/aria-orchestrator}"
LANES="$ORCH_HOME/lanes"
PREFIX="orch-"
mkdir -p "$LANES"

_sess(){ printf '%s%s' "$PREFIX" "$1"; }
_lanedir(){ local d="$LANES/$1"; mkdir -p "$d"; printf '%s' "$d"; }
_live(){ tmux has-session -t "$(_sess "$1")" 2>/dev/null; }

# Pop a real macOS terminal WINDOW attached to the lane's tmux session, so you
# can watch/intervene. The session itself is created detached first (below), so
# closing this window never kills the lane or the orchestrator's control —
# reattach anytime with `tmux attach -t orch-<lane>`. Prefers iTerm if running.
_open_window(){
  local s; s=$(_sess "$1")
  command -v osascript >/dev/null 2>&1 || return 1
  # Prefer iTerm if installed; fall back to Terminal.app if iTerm scripting fails
  # (e.g. first-run automation consent not yet granted).
  if [ -d "/Applications/iTerm.app" ]; then
    if osascript >/dev/null 2>&1 <<OSA
tell application "iTerm"
  create window with default profile command "tmux attach -t $s"
  activate
end tell
OSA
    then return 0; fi
    echo "   (iTerm didn't open — likely the one-time 'allow automation' prompt; approve it, or it'll use Terminal)" >&2
  fi
  osascript >/dev/null 2>&1 <<OSA || return 1
tell application "Terminal"
  do script "tmux attach -t $s"
  activate
end tell
OSA
}

# refuse destructive dispatches unless forced
_guard(){
  case "$1" in
    *deploy*|*restart*|*"rm -rf"*|*"git push"*|*shutdown*|*reboot*|*"swap_model"*) return 1;;
  esac
  return 0
}

cmd_spawn(){ # spawn [--headless] [--cwd <dir>] <lane> [command...]   (default cmd: claude; pops a window)
  local window=1 cwd="" ident=""
  while :; do
    case "${1:-}" in
      --headless) window=0; shift;;
      --window)   window=1; shift;;
      --cwd)      cwd="$2"; shift 2;;
      --identity) ident="$2"; shift 2;;   # path to a system-prompt file → lane boots knowing it's managed
      --claude-args) cargs="$2"; shift 2;;  # extra flags appended to claude (e.g. --permission-mode acceptEdits)
      *) break;;
    esac
  done
  local lane="$1"; shift || true
  local run="${*:-claude}"
  # An identity file makes this a managed claude lane: inject it into the system prompt.
  [ -n "$ident" ] && run="claude --append-system-prompt-file $ident ${cargs:-}"
  local s d; s=$(_sess "$lane"); d=$(_lanedir "$lane")
  if _live "$lane"; then echo "lane '$lane' already live ($s)"; return 0; fi
  # Create DETACHED first so control is robust regardless of the window.
  if [ -n "$cwd" ]; then tmux new -d -s "$s" -c "$cwd" "$run"; else tmux new -d -s "$s" "$run"; fi
  printf '%s\tSPAWN\t%s\n' "$(date '+%F %T')" "$run" >> "$d/DISPATCH.log"
  [ -f "$d/STATUS.md" ] || printf '# lane %s — status\n\n(idle, just spawned)\n' "$lane" > "$d/STATUS.md"
  echo "🟢 spawned lane '$lane' → tmux $s running: $run"
  if [ "$window" -eq 1 ]; then
    if _open_window "$lane"; then
      echo "   🪟 opened a terminal window attached to the lane (close it anytime — the lane keeps running)"
    else
      echo "   (no GUI window opened; session is live headless — attach with: tmux attach -t $s)"
    fi
  fi
}

cmd_send(){ # send [--force] <lane> <text...>
  local force=0; if [ "${1:-}" = "--force" ]; then force=1; shift; fi
  local lane="$1"; shift; local text="$*"
  local s d; s=$(_sess "$lane"); d=$(_lanedir "$lane")
  _live "$lane" || { echo "✗ lane '$lane' not live; \`orch.sh spawn $lane\` first"; return 2; }
  if [ "$force" -eq 0 ] && ! _guard "$text"; then
    echo "⚠ refused: \"$text\" looks destructive (deploy/restart/rm/push/shutdown)."
    echo "  Re-run with --force if you truly mean it (restart stays maintainer-gated)."; return 3
  fi
  tmux send-keys -t "$s" "$text" Enter
  printf '%s\tSEND\t%s\n' "$(date '+%F %T')" "$text" >> "$d/DISPATCH.log"
  echo "→ dispatched to '$lane': $text"
}

cmd_read(){ # read <lane> [N]   (glance at the lane's screen; state lives in STATUS.md)
  local lane="$1"; local n="${2:-20}"
  _live "$lane" || { echo "✗ lane '$lane' not live"; return 2; }
  tmux capture-pane -t "$(_sess "$lane")" -p | grep -v '^[[:space:]]*$' | tail -n "$n"
}

cmd_report(){ # report <lane> <status text...>   (lanes/subagents publish state here)
  local lane="$1"; shift; local d; d=$(_lanedir "$lane")
  { printf '# lane %s — status  (%s)\n\n' "$lane" "$(date '+%F %T')"; printf '%s\n' "$*"; } > "$d/STATUS.md"
  echo "📝 status updated for '$lane'"
}

cmd_status(){ # status   (unified view: tmux lanes + spawned lanes)
  echo "=== orchestrator lanes ($LANES) ==="
  local any=0
  for d in "$LANES"/*/; do
    [ -d "$d" ] || continue; any=1
    local lane; lane=$(basename "$d")
    local mark; if _live "$lane"; then mark="🟢 live(tmux)"; else mark="⚪ stopped/spawned"; fi
    local last; last=$(tail -1 "$d/DISPATCH.log" 2>/dev/null | cut -f1,2,3 | tr '\t' ' ')
    echo "── $lane   [$mark]   last-dispatch: ${last:-none}"
    [ -f "$d/STATUS.md" ] && sed -n '3,7p' "$d/STATUS.md" | sed 's/^/      /'
  done
  [ "$any" = 1 ] || echo "(no lanes yet — orch.sh spawn <lane> [cmd])"
}

cmd_stop(){ # stop <lane>
  local lane="$1"
  if tmux kill-session -t "$(_sess "$lane")" 2>/dev/null; then echo "⏹ stopped '$lane'"; else echo "'$lane' not live"; fi
}

cmd_list(){ tmux ls 2>/dev/null | grep "^${PREFIX}" || echo "(no orchestrator tmux lanes)"; }

cmd_resume(){ # resume [--headless] [--cwd <dir>] [--lane <name>] <session-id> [<session-id>...]
  # Reopen one or more Claude Code sessions AS tmux lanes, so this terminal can
  # drive them (send/read/status) — the controllable version of spawning bare
  # `claude --resume` windows. Pair with the cc-session-resume skill to get IDs.
  local hl="" lane_override="" cwd="$HOME"
  while :; do
    case "${1:-}" in
      --headless) hl="--headless"; shift;;
      --cwd)      cwd="$2"; shift 2;;
      --lane)     lane_override="$2"; shift 2;;
      *) break;;
    esac
  done
  [ -n "${1:-}" ] || { echo "usage: orch.sh resume [--headless] [--cwd <dir>] [--lane <name>] <session-id> [<session-id>...]"; return 1; }
  local n=$# i=0 lane
  for sid in "$@"; do
    i=$((i+1))
    if [ -n "$lane_override" ]; then
      if [ "$n" -gt 1 ]; then lane="${lane_override}-${i}"; else lane="$lane_override"; fi
    else
      lane="r-${sid:0:8}"   # short, recognizable lane from the session id
    fi
    echo "↻ resuming $sid as lane '$lane'"
    cmd_spawn $hl --cwd "$cwd" "$lane" claude --resume "$sid"
  done
  echo "→ drive: orch.sh send <lane> \"<text>\"  |  watch: orch.sh read <lane>  |  board: orch.sh status"
}

case "${1:-}" in
  spawn)  shift; cmd_spawn "$@";;
  resume) shift; cmd_resume "$@";;
  send)   shift; cmd_send "$@";;
  read)   shift; cmd_read "$@";;
  report) shift; cmd_report "$@";;
  status) shift; cmd_status "$@";;
  stop)   shift; cmd_stop "$@";;
  list)   shift; cmd_list "$@";;
  *) echo "usage: orch.sh {spawn <lane> [cmd] | resume [--headless] [--lane <name>] <session-id>... | send [--force] <lane> <text> | read <lane> [N] | report <lane> <text> | status | stop <lane> | list}"; exit 1;;
esac
