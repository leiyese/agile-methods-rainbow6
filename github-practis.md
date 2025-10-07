# GitHub Workflow Practice Guide

## ✅ 1. Pick a Ticket
- Start by selecting a ticket from our JIRA board.
- Make sure it's assigned to you and set to "In Progress."

## 🔄 2. Update Your Local Repository
In your terminal, navigate to the project root folder, then pull the latest changes from GitHub:
```bash
git fetch --all
git pull
```

This ensures your local repository is up to date with all active branches.

## 🧩 3. Check Your Current Status
Run:
```bash
git status
```

If you have uncommitted files, either:
- 💾 Commit them if important, or
- 🧺 Stash them temporarily:
```bash
git stash
```

To bring them back later:
```bash
git stash pop
```

⚠️ Note: git stash will overwrite your previous stash if you use it again without popping the last one.

## 🌿 4. Switch to the dev Branch
```bash
git checkout dev
git pull
```

The dev branch is our shared working branch.
Always make sure your work starts from the latest version of dev.
🚫 Do not commit directly to dev — always use a separate feature branch.

## 🌱 5. Create a New Feature Branch
Create a branch for your specific task:
```bash
git checkout -b <branch-name>
```

Use clear, descriptive names that describe what you're doing, for example:
- FE-fix-chat-component
- BE-database-config

## 💻 6. Start Coding
Work on your feature or fix.
Try to commit small, stable changes with clear, descriptive commit messages:
```bash
git add .
git commit -m "Fix: adjusted chat component scroll behavior"
```

Avoid committing incomplete or broken code — keep commits meaningful and testable.

## 🚀 7. Push Your Branch
When your work is ready:
```bash
git push -u origin <branch-name>
```

This makes your branch available for teammates to pull, test, and review.

## 🔀 8. Open a Pull Request (PR)
On GitHub:
- Create a Pull Request from your branch → dev
- ✅ Make sure the target branch is dev, not main
- Add a short summary describing what your changes do
- Request a reviewer from the team

Once approved, the reviewer will confirm and merge the PR.

## 🧭 9. After Merge
After your PR has been merged into dev:
- Update the JIRA ticket status to "Code Review Done" or "Ready for Testing"
- Pull the latest changes to stay up to date:
```bash
git checkout dev
git pull
```

## 🧾 Quick Summary

| Step | Action | Command |
|------|--------|---------|
| 1 | Pick a JIRA ticket | — |
| 2 | Update repo | `git fetch --all && git pull` |
| 3 | Check status | `git status` |
| 4 | Switch to dev | `git checkout dev && git pull` |
| 5 | Create branch | `git checkout -b <branch>` |
| 6 | Code & commit | `git commit -m "..."` |
| 7 | Push branch | `git push -u origin <branch>` |
| 8 | Create PR → dev | via GitHub |
| 9 | Pull updated dev | `git pull` |
