#!/usr/bin/env bash

set -u

REPO_DIR="/home/ktj/Machine_Learning_Project"
BRANCH="main"
REMOTE="origin"
DEBOUNCE_SECONDS=3

cd "$REPO_DIR" || exit 1

if ! command -v inotifywait >/dev/null 2>&1; then
    echo "[auto-git] inotifywait is not installed."
    exit 1
fi

sync_remote() {
    git fetch "$REMOTE" "$BRANCH" || return 1

    local local_head
    local remote_head
    local_head="$(git rev-parse HEAD)"
    remote_head="$(git rev-parse "$REMOTE/$BRANCH")"

    if [ "$local_head" = "$remote_head" ]; then
        return 0
    fi

    echo "[auto-git] Remote changed. Rebasing local work onto $REMOTE/$BRANCH..."
    if git pull --rebase --autostash "$REMOTE" "$BRANCH"; then
        return 0
    fi

    echo "[auto-git] Rebase failed. Resolve conflicts manually before auto push continues."
    git rebase --abort >/dev/null 2>&1 || true
    return 1
}

commit_and_push() {
    cd "$REPO_DIR" || return 1

    if ! sync_remote; then
        return 1
    fi

    if git diff --quiet && git diff --cached --quiet; then
        echo "[auto-git] No meaningful changes."
        return 0
    fi

    git add -A

    if git diff --cached --quiet; then
        echo "[auto-git] Nothing staged after filtering ignored files."
        return 0
    fi

    local commit_msg
    commit_msg="auto: update $(date '+%Y-%m-%d %H:%M:%S')"

    if ! git commit -m "$commit_msg"; then
        echo "[auto-git] Commit failed."
        return 1
    fi

    if ! sync_remote; then
        return 1
    fi

    if git push "$REMOTE" "$BRANCH"; then
        echo "[auto-git] Pushed to $REMOTE/$BRANCH"
    else
        echo "[auto-git] Push failed. Check network/auth and retry manually."
        return 1
    fi
}

echo "[auto-git] Watching:"
echo "  repo   : $REPO_DIR"
echo "  remote : $REMOTE/$BRANCH"

sync_remote || true

while true; do
    inotifywait -r -e modify,create,delete,move \
        --exclude '(\.git|build|install|log|__pycache__|\.vscode|.*~|.*\.swp)' \
        "$REPO_DIR"

    echo "[auto-git] Change detected. Waiting $DEBOUNCE_SECONDS seconds..."
    sleep "$DEBOUNCE_SECONDS"

    commit_and_push || true
done
