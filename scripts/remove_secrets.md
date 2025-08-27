Remove sensitive keys from git history

If you accidentally committed API keys, follow these steps locally (read carefully):

1. Rotate/revoke the exposed keys immediately with provider consoles.
2. Install `git-filter-repo` (recommended) or use `bfg`.


Example using git-filter-repo to remove `api_keys.json` and `.env` from history:

```powershell
# Install: pip install git-filter-repo
git clone --mirror https://github.com/your-user/ITM_Translate.git
cd ITM_Translate.git
# Remove files from all history
git filter-repo --invert-paths --paths api_keys.json --paths .env
git push --force --mirror https://github.com/your-user/ITM_Translate.git
```

Notes:
- This rewrites history; coordinate with contributors.
- After rewriting, ask all collaborators to reclone.
