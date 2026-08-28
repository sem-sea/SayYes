#!/usr/bin/env bash
# Apply the repository description, homepage, and topics from docs/REPO-SETTINGS.md.
#
# These three fields live in GitHub settings rather than in the tree, and they
# carry more search weight than anything in the README. This script keeps their
# values under version control and applies them in one command, so they survive
# a transfer and stay reviewable in a diff.
#
#   ./scripts/apply_repo_settings.sh              # apply to sem-sea/SayYes
#   ./scripts/apply_repo_settings.sh owner/repo   # apply elsewhere
#   DRY_RUN=1 ./scripts/apply_repo_settings.sh    # print what would be sent
#
# Auth, in order of preference:
#   1. the gh CLI, when installed and logged in
#   2. GH_TOKEN or GITHUB_TOKEN with the `repo` scope
#
# Create a token at https://github.com/settings/tokens with `public_repo`
# (or `repo` for a private repository).

set -euo pipefail

REPO="${1:-sem-sea/SayYes}"

DESCRIPTION="yesand: positive prompting for agent instructions. An Agent Skill that rewrites prohibitions in your system prompt, CLAUDE.md or AGENTS.md into the action to take, following Anthropic and Google prompt-engineering guidance. Ships a preregistered instruction-following benchmark. Claude Code, Cursor, Codex and 74 more."

HOMEPAGE="https://github.com/${REPO}/blob/main/docs/METHODOLOGY.md"

# GitHub allows 20 topics. Lowercase, hyphenated, 50 characters or fewer each.
TOPICS=(
  prompt-engineering
  positive-prompting
  instruction-following
  agent-skills
  agent-skill
  claude-skills
  claude-code
  claude-code-plugin
  claude
  anthropic
  llm
  system-prompt
  prompt-optimization
  ai-agents
  benchmark
  llm-evaluation
  cursor
  codex
)

# --- checks ---------------------------------------------------------------

if [ "${#DESCRIPTION}" -gt 350 ]; then
  echo "description is ${#DESCRIPTION} characters; GitHub caps it at 350" >&2
  exit 1
fi

if [ "${#TOPICS[@]}" -gt 20 ]; then
  echo "topic list holds ${#TOPICS[@]}; GitHub caps it at 20" >&2
  exit 1
fi

for topic in "${TOPICS[@]}"; do
  if ! [[ "$topic" =~ ^[a-z0-9][a-z0-9-]{0,49}$ ]]; then
    echo "topic '$topic' should be lowercase alphanumeric with hyphens, 50 chars or fewer" >&2
    exit 1
  fi
done

topics_json=$(printf '%s\n' "${TOPICS[@]}" | jq -R . | jq -sc '{names: .}')
repo_json=$(jq -nc --arg d "$DESCRIPTION" --arg h "$HOMEPAGE" '{description: $d, homepage: $h}')

echo "repository : $REPO"
echo "description: ${#DESCRIPTION}/350 characters"
echo "topics     : ${#TOPICS[@]}/20"
echo

if [ -n "${DRY_RUN:-}" ]; then
  echo "DRY_RUN set, printing payloads instead of sending them."
  echo; echo "PATCH /repos/$REPO"; echo "$repo_json" | jq .
  echo; echo "PUT /repos/$REPO/topics"; echo "$topics_json" | jq .
  exit 0
fi

# --- apply ----------------------------------------------------------------

if command -v gh >/dev/null 2>&1 && gh auth status >/dev/null 2>&1; then
  echo "using the gh CLI"
  echo "$repo_json"   | gh api -X PATCH "repos/$REPO" --input - > /dev/null
  echo "$topics_json" | gh api -X PUT "repos/$REPO/topics" --input - > /dev/null
else
  TOKEN="${GH_TOKEN:-${GITHUB_TOKEN:-}}"
  if [ -z "$TOKEN" ]; then
    echo "install the gh CLI and run 'gh auth login', or set GH_TOKEN to a token with the repo scope" >&2
    exit 1
  fi
  echo "using the REST API with a token"
  api() {
    local method="$1" path="$2" body="$3" code
    code=$(curl -sS -o /tmp/ghout.$$ -w '%{http_code}' \
      -X "$method" "https://api.github.com/$path" \
      -H "Authorization: Bearer $TOKEN" \
      -H "Accept: application/vnd.github+json" \
      -H "X-GitHub-Api-Version: 2022-11-28" \
      -d "$body")
    if [ "$code" -ge 300 ]; then
      echo "$method /$path returned $code" >&2
      jq -r '.message // .' /tmp/ghout.$$ >&2 2>/dev/null || cat /tmp/ghout.$$ >&2
      rm -f /tmp/ghout.$$
      exit 1
    fi
    rm -f /tmp/ghout.$$
  }
  api PATCH "repos/$REPO" "$repo_json"
  api PUT "repos/$REPO/topics" "$topics_json"
fi

echo "applied. verifying:"
echo
if command -v gh >/dev/null 2>&1 && gh auth status >/dev/null 2>&1; then
  gh api "repos/$REPO" --jq '"description: \(.description)\nhomepage   : \(.homepage)\ntopics     : \(.topics | join(", "))"'
else
  curl -sS "https://api.github.com/repos/$REPO" \
    -H "Authorization: Bearer ${GH_TOKEN:-$GITHUB_TOKEN}" \
    -H "Accept: application/vnd.github+json" \
  | jq -r '"description: \(.description)\nhomepage   : \(.homepage)\ntopics     : \(.topics | join(", "))"'
fi
