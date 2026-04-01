#!/bin/bash
# ═══════════════════════════════════════════════════════════════
# GOLDEN AI STRATEGY — Office Workspace
# 7 Division Windows · by Muhamad Ridwanjr
# ═══════════════════════════════════════════════════════════════

BASE="$HOME/gasstrategyai"
SESSION="GAS"
unset ANTHROPIC_API_KEY

# Kill existing session
tmux kill-session -t $SESSION 2>/dev/null
sleep 0.5

# WIN 0: Terminal launcher (auto-start)
tmux new-session -d -s $SESSION -n "0-terminal" -x 220 -y 55
tmux send-keys -t $SESSION:"0-terminal" \
  "cd $BASE && bash gas-terminal.sh" Enter

# Division windows (standby)
declare -a wins=(
  "1-engineering:Engineering  | gateway · terminal-be/fe · web"
  "2-data:Data          | mt5-ws · scrapers · rag · realtime"
  "3-trading:Trading      | signal · quant · strategy · risk"
  "4-platform:Platform     | auth · billing · user · telegram"
  "5-devops:DevOps       | docker · nginx · ai-orchestrator"
  "6-security:Security     | firewall · audit · rate-limit"
)

CORAL='\033[38;2;205;95;70m'
CREAM='\033[1m\033[38;2;245;235;215m'
CYAN='\033[38;2;80;220;220m'
DIM='\033[2m'
R='\033[0m'

for entry in "${wins[@]}"; do
  wname=${entry%%:*}
  label=${entry#*:}
  tmux new-window -t $SESSION -n "$wname"
  tmux send-keys -t $SESSION:"$wname" \
    "cd $BASE && clear && echo '' && \
     printf '${CORAL}  ═══════════════════════════════════════════════════${R}\n' && \
     printf '  ${CREAM}$label${R}\n' && \
     printf '${CORAL}  ═══════════════════════════════════════════════════${R}\n' && \
     echo '' && \
     printf '  ${DIM}Status: STANDBY — waiting for task assignment${R}\n' && \
     echo '' && \
     printf '  ${CYAN}Activate: bash gas-terminal.sh → pick division number${R}\n' && \
     echo '' && \
     printf '  ${DIM}Docs: cat divisions/$(echo \"$label\" | cut -d\" \" -f1 | tr a-z A-Z)_MANAGER.md${R}\n'" Enter
done

tmux select-window -t $SESSION:"0-terminal"

# Print launch info
printf '\n'
printf '\033[38;2;205;95;70m  ╔══════════════════════════════════════════════════════╗\033[0m\n'
printf '\033[38;2;205;95;70m  ║\033[0m  \033[1m\033[38;2;245;235;215mGOLDEN AI STRATEGY — Office Open\033[0m                  \033[38;2;205;95;70m║\033[0m\n'
printf '\033[38;2;205;95;70m  ╠══════════════════════════════════════════════════════╣\033[0m\n'
printf '\033[38;2;205;95;70m  ║\033[0m  WIN 0  \033[38;2;255;195;0mterminal\033[0m   ← Main launcher (auto-started)     \033[38;2;205;95;70m║\033[0m\n'
printf '\033[38;2;205;95;70m  ║\033[0m  WIN 1  engineering  ← gateway · terminal · frontend  \033[38;2;205;95;70m║\033[0m\n'
printf '\033[38;2;205;95;70m  ║\033[0m  WIN 2  data         ← mt5 · scrapers · rag           \033[38;2;205;95;70m║\033[0m\n'
printf '\033[38;2;205;95;70m  ║\033[0m  WIN 3  trading      ← signal · quant · strategy      \033[38;2;205;95;70m║\033[0m\n'
printf '\033[38;2;205;95;70m  ║\033[0m  WIN 4  platform     ← auth · billing · telegram       \033[38;2;205;95;70m║\033[0m\n'
printf '\033[38;2;205;95;70m  ║\033[0m  WIN 5  devops       ← docker · nginx · monitoring     \033[38;2;205;95;70m║\033[0m\n'
printf '\033[38;2;205;95;70m  ║\033[0m  WIN 6  security     ← firewall · audit · rate-limit   \033[38;2;205;95;70m║\033[0m\n'
printf '\033[38;2;205;95;70m  ╠══════════════════════════════════════════════════════╣\033[0m\n'
printf '\033[38;2;205;95;70m  ║\033[0m  \033[2mCtrl+b [0-6] navigate │ Ctrl+b d detach\033[0m           \033[38;2;205;95;70m║\033[0m\n'
printf '\033[38;2;205;95;70m  ╚══════════════════════════════════════════════════════╝\033[0m\n'
printf '\n'

tmux attach -t $SESSION
