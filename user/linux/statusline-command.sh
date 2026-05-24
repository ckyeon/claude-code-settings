#!/usr/bin/env bash
# Two-line status line for Claude Code.
# Line 1: code context (cwd, branch, worktree, diff, PR)
# Line 2: session state (model·effort, context progress bar)

input=$(cat)

cwd=$(echo "$input" | jq -r '.workspace.current_dir // empty')
model=$(echo "$input" | jq -r '.model.display_name // empty')
used=$(echo "$input" | jq -r '.context_window.used_percentage // empty')
effort=$(echo "$input" | jq -r '.effort.level // empty')
git_wt=$(echo "$input" | jq -r '.workspace.git_worktree // empty')
pr_num=$(echo "$input" | jq -r '.pr.number // empty')
pr_state=$(echo "$input" | jq -r '.pr.review_state // empty')

blue='\033[34m'; magenta='\033[35m'; yellow='\033[33m'
cyan='\033[36m'; green='\033[32m'; red='\033[31m'
grey='\033[90m'; bold='\033[1m'; reset='\033[0m'

# === Line 1: code context ===
line1=""

if [ -n "$cwd" ]; then
  line1="${blue}${cwd/#$HOME/\~}${reset}"
fi

if [ -n "$cwd" ]; then
  branch=$(git -C "$cwd" --no-optional-locks symbolic-ref --short HEAD 2>/dev/null)
  [ -n "$branch" ] && line1="${line1}  ${magenta}${branch}${reset}"
fi

if [ -n "$git_wt" ]; then
  line1="${line1}  ${cyan}[wt:${git_wt}]${reset}"
fi

if [ -n "$cwd" ]; then
  diff_stat=$(git -C "$cwd" --no-optional-locks diff --shortstat 2>/dev/null)
  if [ -n "$diff_stat" ]; then
    ins=$(echo "$diff_stat" | grep -o '[0-9]* insertion' | grep -o '[0-9]*')
    del=$(echo "$diff_stat" | grep -o '[0-9]* deletion' | grep -o '[0-9]*')
    diff_str=""
    [ -n "$ins" ] && diff_str="+${ins}"
    [ -n "$del" ] && diff_str="${diff_str}-${del}"
    [ -n "$diff_str" ] && line1="${line1}  ${yellow}${diff_str}${reset}"
  fi
fi

if [ -n "$pr_num" ]; then
  pr_color="$grey"
  case "$pr_state" in
    approved)          pr_color="$green" ;;
    pending)           pr_color="$yellow" ;;
    changes_requested) pr_color="$red" ;;
    draft)             pr_color="$grey" ;;
  esac
  pr_text="PR#${pr_num}"
  [ -n "$pr_state" ] && pr_text="${pr_text} ${pr_state}"
  line1="${line1}  ${pr_color}${pr_text}${reset}"
fi

# === Line 2: session state ===
line2=""

if [ -n "$model" ]; then
  line2="${model}"
  [ -n "$effort" ] && line2="${line2} · ${effort}"
fi

if [ -n "$used" ]; then
  pct=$(printf '%.0f' "$used")
  bar_width=20
  filled=$((pct * bar_width / 100))
  empty=$((bar_width - filled))

  if [ "$pct" -ge 90 ]; then bar_color="$red"
  elif [ "$pct" -ge 70 ]; then bar_color="$yellow"
  else bar_color="$green"; fi

  bar=""
  [ "$filled" -gt 0 ] && printf -v fill "%${filled}s" && bar="${fill// /█}"
  [ "$empty" -gt 0 ] && printf -v pad "%${empty}s" && bar="${bar}${pad// /░}"

  line2="${line2}  ${bar_color}${bar} ${pct}%${reset}"
fi

# === Output ===
printf '%b\n' "$line1"
[ -n "$line2" ] && printf '%b' "$line2"
