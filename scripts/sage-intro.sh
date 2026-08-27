#!/usr/bin/env bash
# sage-intro-solid.sh — animated ASCII intro for the Sage onboarding skill
# "monolith" variant: solid block arch (aperture as negative space) + figlet wordmark
# zero dependencies · bash 3.2+ · ~4.8s · designed for dark-background terminals
#
# usage:
#   sage-intro-solid.sh              animate (falls back to static card if not a TTY)
#   sage-intro-solid.sh --static     print the final card only
#   sage-intro-solid.sh --dump-all   emit every frame separated by \f (for previews)

MODE="animate"
case "${1:-}" in
  --static)   MODE="static" ;;
  --dump-all) MODE="dump" ;;
esac

# ---------------------------------------------------------------- colors
ESC=$(printf '\033')
R="${ESC}[0m"
if [ -n "${NO_COLOR:-}" ]; then
  TB=""; TD=""; TM=""; CR=""; CD=""; GD=""; GB=""; RL=""; BW=""
  G1=""; G2=""; G3=""
elif [ "${COLORTERM:-}" = "truecolor" ] || [ "${COLORTERM:-}" = "24bit" ] || [ -n "${WT_SESSION:-}" ] || [ "$MODE" = "dump" ]; then
  TB="${ESC}[38;2;35;178;152m"     # bright teal (accent on brand #0E6A5C)
  TM="${ESC}[38;2;22;134;116m"     # mid teal    (arch structure)
  TD="${ESC}[38;2;13;92;80m"       # dim teal    (water trough)
  CR="${ESC}[1m${ESC}[38;2;251;247;239m"  # cream, bold (wordmark)  #FBF7EF
  CD="${ESC}[38;2;214;207;192m"    # dim cream   (tagline, question)
  GD="${ESC}[38;2;178;146;84m"     # dim gold    (sun rising)
  GB="${ESC}[38;2;242;217;160m"    # bright gold (sun risen)
  RL="${ESC}[38;2;90;90;86m"       # rule / faint
  BW="${ESC}[1m${ESC}[38;2;255;255;255m"  # flash white
  G1="${ESC}[38;2;58;62;61m"; G2="${ESC}[38;2;84;96;92m"; G3="${ESC}[38;2;110;128;120m"
else
  TB="${ESC}[38;5;43m";  TM="${ESC}[38;5;36m";  TD="${ESC}[38;5;29m"
  CR="${ESC}[1m${ESC}[38;5;230m"; CD="${ESC}[38;5;250m"
  GD="${ESC}[38;5;136m"; GB="${ESC}[38;5;222m"; RL="${ESC}[38;5;240m"
  BW="${ESC}[1m${ESC}[38;5;231m"
  G1="${ESC}[38;5;237m"; G2="${ESC}[38;5;240m"; G3="${ESC}[38;5;243m"
fi

# ---------------------------------------------------------------- geometry
IND="  "                       # left indent for the whole card
GAP="    "                     # gap between arch (21 cols) and right-hand text
INNER="             "          # 13 spaces, aperture interior
FRAME_H=15
LAST_FRAME=112

# water: 13 cells, 4 phases, drifting right one cell per phase
WP0="~ . = . ~ . = . ~ . = . ~"
WP1=". ~ . = . ~ . = . ~ . = ."
WP2="= . ~ . = . ~ . = . ~ . ="
WP3=". = . ~ . = . ~ . = . ~ ."

build_water() {  # $1 = phase token string -> colored row in REPLY_WATER
  local out="" t
  for t in $1; do
    case "$t" in
      "~") out="${out}${TD}~" ;;
      "=") out="${out}${TB}≈" ;;
      ".") out="${out} " ;;
    esac
  done
  REPLY_WATER="${out}${R}"
}
build_water "$WP0"; W0="$REPLY_WATER"
build_water "$WP1"; W1="$REPLY_WATER"
build_water "$WP2"; W2="$REPLY_WATER"
build_water "$WP3"; W3="$REPLY_WATER"

# figlet "small" — SAGE (letters end at cols 5 / 13 / 20 / 26)
FG0=' ___     _     ___   ___ '
FG1='/ __|   /_\   / __| | __|'
FG2='\__ \  / _ \ | (_ | | _| '
FG3='|___/ /_/ \_\ \___| |___|'

TAGLINE="Your AI needs an if-statement."

# five decisions, one per Sage kind: yes/no · scale · choice · sort · tags
Q1='"is this tool call safe to auto-run?"'
Q2='"how well does this PR match its spec?"'
Q3='"which model tier does this need?"'
Q4='"1,000 open tickets: which one first?"'
Q5='"what kind of data did the user paste?"'
QLEN=37   # length of Q1, the typewritten one
QPAD=39   # questions pad to this so the arrows column-align

# rapid-fire line: question+arrow at $5, answer flashes at $6, settles at $6+2
# uses caller's $f; args: q aval conf ms qframe aframe
rapid() {
  REPLY_D=""
  [ "$f" -lt "$5" ] && return
  REPLY_D="${CD}$(printf "%-${QPAD}s" "$1")${R}  ${TM}──▶${R}  "
  if [ "$f" -ge "$6" ] && [ "$f" -lt $(( $6 + 2 )) ]; then
    REPLY_D="${REPLY_D}${BW}$2${R}"
  elif [ "$f" -ge $(( $6 + 2 )) ]; then
    REPLY_D="${REPLY_D}${TB}${ESC}[1m$2${R}${RL} · ${R}${CD}confidence ${R}${CR}$3${R}${RL} · $4${R}"
  fi
}

# ---------------------------------------------------------------- frame builder
draw_frame() {  # $1 = frame number -> sets OUT (11 lines, \n-terminated each)
  local f=$1
  local AC sun water_a water_b w0 w1 w2 w3 wl tag d1 d2 d3 d4 d5 conf p n

  # arch color ramp (fade-in), then settle on dim teal (structure stays quiet)
  if   [ "$f" -le 1 ]; then AC="$G1"
  elif [ "$f" -eq 2 ]; then AC="$G2"
  elif [ "$f" -eq 3 ]; then AC="$G3"
  elif [ "$f" -eq 4 ]; then AC="$TD"
  else AC="$TM"; fi

  # sun
  if   [ "$f" -lt 6 ];  then sun=" "
  elif [ "$f" -lt 10 ]; then sun="${GD}·${R}"
  elif [ "$f" -lt 14 ]; then sun="${GD}•${R}"
  elif [ "$f" -lt 18 ]; then sun="${GD}●${R}"
  elif [ "$f" -lt 102 ]; then sun="${GB}●${R}"
  else # gentle pulse in the outro
    if [ $(( (f / 3) % 2 )) -eq 0 ]; then sun="${GB}●${R}"; else sun="${GD}●${R}"; fi
  fi

  # water phase
  if [ "$f" -lt 6 ]; then
    water_a="$INNER"; water_b="$INNER"
  else
    if [ "$f" -lt 30 ]; then p=$(( f % 4 ))
    elif [ "$f" -lt 67 ]; then p=$(( (f / 3) % 4 ))
    else p=$(( f % 4 )); fi
    case $p in
      0) water_a="$W0"; water_b="$W2" ;;
      1) water_a="$W1"; water_b="$W3" ;;
      2) water_a="$W2"; water_b="$W0" ;;
      3) water_a="$W3"; water_b="$W1" ;;
    esac
  fi

  # wordmark letters land one by one (figlet column cuts: 5, 13, 20, 26)
  if   [ "$f" -lt 20 ]; then wl=0
  elif [ "$f" -lt 22 ]; then wl=5
  elif [ "$f" -lt 24 ]; then wl=13
  elif [ "$f" -lt 26 ]; then wl=20
  else wl=26; fi
  if [ "$wl" -gt 0 ]; then
    w0="${CR}${FG0:0:$wl}${R}"; w1="${CR}${FG1:0:$wl}${R}"
    w2="${CR}${FG2:0:$wl}${R}"; w3="${CR}${FG3:0:$wl}${R}"
  else
    w0=""; w1=""; w2=""; w3=""
  fi

  tag=""; [ "$f" -ge 29 ] && tag="${CD}${TAGLINE}${R}"

  # decision 1 teaches the pattern: typewriter, flash, confidence counts up
  d1=""
  if [ "$f" -ge 30 ] && [ "$f" -lt 68 ]; then
    n=$(( f - 29 )); [ "$n" -gt "$QLEN" ] && n=$QLEN
    d1="${CD}${Q1:0:$n}${R}"
  elif [ "$f" -ge 68 ]; then
    d1="${CD}$(printf "%-${QPAD}s" "$Q1")${R}  ${TM}──▶${R}  "
    if [ "$f" -eq 70 ]; then d1="${d1}${BW}yes${R}"
    elif [ "$f" -ge 71 ]; then
      if   [ "$f" -eq 71 ]; then conf="0.62"
      elif [ "$f" -eq 72 ]; then conf="0.87"
      else conf="0.94"; fi
      d1="${d1}${TB}${ESC}[1myes${R}${RL} · ${R}${CD}confidence ${R}${CR}${conf}${R}"
      [ "$f" -ge 74 ] && d1="${d1}${RL} · 212ms${R}"
    fi
  fi

  # decisions 2-5 fire rapidly, accelerating — the speed is the point
  rapid "$Q2" "4/10"  "0.88" "198ms" 78 81; d2="$REPLY_D"
  rapid "$Q3" "small" "0.91" "187ms" 85 87; d3="$REPLY_D"
  rapid "$Q4" "#4712" "0.83" "341ms" 91 93; d4="$REPLY_D"
  rapid "$Q5" "pii"   "0.97" "178ms" 96 98; d5="$REPLY_D"

  OUT=""
  OUT="${OUT}\n"
  OUT="${OUT}${IND}${AC}█████████████████████${R}\n"
  OUT="${OUT}${IND}${AC}████████▀▀▀▀▀████████${R}\n"
  OUT="${OUT}${IND}${AC}█████▀         ▀█████${R}${GAP}${w0}\n"
  OUT="${OUT}${IND}${AC}████▀           ▀████${R}${GAP}${w1}\n"
  OUT="${OUT}${IND}${AC}████${R}      ${sun}      ${AC}████${R}${GAP}${w2}\n"
  OUT="${OUT}${IND}${AC}████${R}${INNER}${AC}████${R}${GAP}${w3}\n"
  OUT="${OUT}${IND}${AC}████${R}${water_a}${AC}████${R}\n"
  OUT="${OUT}${IND}${AC}████${R}${water_b}${AC}████${R}${GAP}${tag}\n"
  OUT="${OUT}\n"
  OUT="${OUT}${IND}${d1}\n"
  OUT="${OUT}${IND}${d2}\n"
  OUT="${OUT}${IND}${d3}\n"
  OUT="${OUT}${IND}${d4}\n"
  OUT="${OUT}${IND}${d5}\n"
}

frame_delay() {  # $1 = frame number -> echoes sleep seconds
  local f=$1
  if   [ "$f" -lt 6 ];  then echo 0.09
  elif [ "$f" -lt 30 ]; then echo 0.08
  elif [ "$f" -lt 67 ]; then echo 0.025
  elif [ "$f" -lt 70 ]; then echo 0.08
  elif [ "$f" -lt 75 ]; then echo 0.09
  else echo 0.08; fi
}

print_frame() {  # print OUT with clear-to-eol on every line
  printf '%b' "${OUT//\\n/${ESC}[K\\n}"
}

# ---------------------------------------------------------------- modes
if [ "$MODE" = "dump" ]; then
  f=0
  while [ "$f" -le "$LAST_FRAME" ]; do
    draw_frame "$f"
    printf '%b' "$OUT"
    printf '\f\n'
    f=$(( f + 1 ))
  done
  exit 0
fi

if [ "$MODE" = "static" ] || [ ! -t 1 ]; then
  draw_frame "$LAST_FRAME"
  printf '%b' "$OUT"
  exit 0
fi

# terminal too narrow to animate cleanly -> static card
cols=$(tput cols 2>/dev/null || echo 80)
if [ "$cols" -lt 79 ]; then
  draw_frame "$LAST_FRAME"
  printf '%b' "$OUT"
  exit 0
fi

cleanup() { printf '%b' "${ESC}[?25h${R}"; }
trap cleanup EXIT INT TERM

printf '%b' "${ESC}[?25l"
f=0
while [ "$f" -le "$LAST_FRAME" ]; do
  draw_frame "$f"
  print_frame
  if [ "$f" -lt "$LAST_FRAME" ]; then
    sleep "$(frame_delay "$f")"
    printf '%b' "${ESC}[${FRAME_H}A"
  fi
  f=$(( f + 1 ))
done
printf '%b' "${ESC}[?25h${R}"
