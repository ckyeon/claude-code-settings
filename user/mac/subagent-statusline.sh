#!/usr/bin/env bash
# Sub-agent status line for Claude Code.
# Receives JSON with tasks array, outputs one JSON line per task.

input=$(cat)

green='\033[32m'; grey='\033[90m'; red='\033[31m'
bold='\033[1m'; reset='\033[0m'

now=$(date +%s)

echo "$input" | jq -c '.tasks[]?' | while IFS= read -r task; do
  id=$(echo "$task" | jq -r '.id')
  name=$(echo "$task" | jq -r '.name // "unnamed"')
  status=$(echo "$task" | jq -r '.status // "unknown"')
  tokens=$(echo "$task" | jq -r '.tokenCount // 0')
  start=$(echo "$task" | jq -r '.startTime // 0')

  case "$status" in
    running)   dot="${green}●${reset}"; stxt="${green}${status}${reset}" ;;
    completed) dot="${grey}●${reset}";  stxt="${grey}${status}${reset}" ;;
    error|failed) dot="${red}●${reset}"; stxt="${red}${status}${reset}" ;;
    *)         dot="${grey}●${reset}";  stxt="${grey}${status}${reset}" ;;
  esac

  if [ "$tokens" -ge 1000 ]; then
    tok_str="$(echo "scale=1; $tokens / 1000" | bc)k"
  else
    tok_str="${tokens}"
  fi

  elapsed=""
  if [ "$start" -gt 0 ]; then
    diff=$((now - start))
    mins=$((diff / 60))
    secs=$((diff % 60))
    if [ "$mins" -gt 0 ]; then
      elapsed="${mins}m ${secs}s"
    else
      elapsed="${secs}s"
    fi
  fi

  content="${dot} ${stxt}  ${bold}${name}${reset}"
  [ -n "$tok_str" ] && [ "$tokens" -gt 0 ] && content="${content}  ${grey}${tok_str} tokens${reset}"
  [ -n "$elapsed" ] && content="${content}  ${grey}${elapsed}${reset}"

  printf '{"id":"%s","content":"%s"}\n' "$id" "$content"
done
