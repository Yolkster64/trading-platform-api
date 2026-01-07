# GitHub API Token Setup Guide

## Overview

This guide walks you through creating and configuring GitHub API tokens for your Trading Platform API.

---

## Step 1: Create a Personal Access Token (PAT)

### Navigate to GitHub Settings

1. Go to https://github.com/settings/tokens
2. Or manually:
   - Click your profile icon (top right)
   - Select "Settings"
   - Go to "Developer settings" (bottom left)
   - Click "Personal access tokens"
   - Click "Tokens (classic)"

### Create New Token

1. Click "Generate new token"
2. Select "Generate new token (classic)"

### Configure Token Permissions

**Token name**: `Trading Platform API`

**Expiration**: 90 days (or your preference)

**Select scopes** (check these boxes):

#### Repository Access (Required)
- ✅ `repo` - Full control of private repositories
  - This includes all repository operations needed
  - Covers: `repo:status`, `repo_deployment`, `public_repo`

#### Additional Recommended Scopes
- ✅ `read:user` - Read user profile data
- ✅ `user:email` - Access email addresses
- ⬜ `admin:repo_hook` - Full control of repository hooks (optional)
- ⬜ `admin:org_hook` - Full control of organization hooks (optional)

**Minimal Setup** (if you only need basic access):
```
✅ repo (all)
✅ read:user
✅ user:email
```

**Full Access** (for complete integration):
```
✅ repo (all)
✅ read:user
✅ user:email
✅ admin:repo_hook
✅ gist
```

### Generate and Copy Token

1. Click "Generate token"
2. **COPY the token immediately** - you won't see it again!
3. It looks like: `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

---

## Step 2: Add Token to .env File

### Edit Your .env File

Open `E:\trading-platform-api\.env` and add:

```env
# GitHub Configuration
GITHUB_API_TOKEN=ghp_your_token_here
GITHUB_OWNER=your-github-username
GITHUB_REPO=your-repo-name
```

### Replace These Values

| Variable | Value | Example |
|----------|-------|---------|
| `GITHUB_API_TOKEN` | Your generated token | `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxx` |
| `GITHUB_OWNER` | Your GitHub username | `john-smith` or `my-company` |
| `GITHUB_REPO` | Target repository name | `trading-platform` or `api-server` |

### Example Configuration

```env
# GitHub Configuration
GITHUB_API_TOKEN=ghp_1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p7q8r9s
GITHUB_OWNER=trading-dev
GITHUB_REPO=trading-platform-api
```

---

## Step 3: Verify Configuration

### Run Verification Script

```bash
cd E:\trading-platform-api
python verify_system.py
```

You should see:
```
GitHub              ✅ CONFIGURED
```

### Test API Access

```bash
python -c "from config import get_config; c = get_config(); print(f'GitHub: {c.github.is_configured()}')"
```

Output:
```
GitHub: True
```

---

## Common Operations

### Get Repository Information

```python
from github import Github
from config import get_config

config = get_config()
g = Github(config.github.api_token)
repo = g.get_user(config.github.owner).get_repo(config.github.repo)

print(f"Repository: {repo.full_name}")
print(f"Stars: {repo.stargazers_count}")
print(f"Language: {repo.language}")
```

### List Repository Issues

```python
issues = repo.get_issues(state='open')
for issue in issues:
    print(f"#{issue.number}: {issue.title}")
```

### List Pull Requests

```python
prs = repo.get_pulls(state='open')
for pr in prs:
    print(f"#{pr.number}: {pr.title}")
```

### Get Repository Stats

```python
print(f"Forks: {repo.forks_count}")
print(f"Watchers: {repo.watchers_count}")
print(f"Open Issues: {repo.open_issues_count}")
print(f"Default Branch: {repo.default_branch}")
```

---

## Token Scopes Explained

### `repo` - Repository Access
- Create, read, update, delete repositories
- Access repository settings
- Manage webhooks
- Required for: Most GitHub operations

### `read:user` - User Profile
- Read user profile information
- Required for: Getting your GitHub identity

### `user:email` - Email Access
- Access your email addresses
- Required for: Email-based operations

### `admin:repo_hook` - Repository Webhooks
- Create and manage repository webhooks
- Required for: GitHub webhook integration

### `gist` - Gist Access
- Create and manage gists
- Required for: Gist operations (usually not needed)

---

## Security Best Practices

### ✅ DO:
- [ ] Keep token in .env (git-ignored)
- [ ] Use specific scopes (don't over-grant)
- [ ] Set expiration (90 days recommended)
- [ ] Rotate tokens regularly
- [ ] Use one token per application
- [ ] Review active tokens monthly

### ❌ DON'T:
- [ ] Commit token to git
- [ ] Share token in chat or email
- [ ] Use same token for multiple apps
- [ ] Disable token expiration
- [ ] Grant more scopes than needed

---

## Troubleshooting

### Token Not Working

**Problem**: `401 Unauthorized` or `Bad credentials`

**Solutions**:
1. Verify token is correct in .env
2. Check token hasn't expired
3. Regenerate new token
4. Verify token has required scopes

### Repository Not Found

**Problem**: `404 Not Found`

**Solutions**:
1. Verify `GITHUB_OWNER` is correct username
2. Verify `GITHUB_REPO` is correct repository name
3. Verify token has `repo` scope
4. Verify you have access to repository

### Rate Limiting

**Problem**: `403 API rate limit exceeded`

**Details**:
- Unauthenticated: 60 requests/hour
- Authenticated: 5,000 requests/hour

**Solution**:
- Ensure token is being used
- Implement caching
- Add request delays

### Token Expiration

**Problem**: Token stopped working after 90 days

**Solution**:
1. Go to https://github.com/settings/tokens
2. Click "Regenerate token"
3. Update .env with new token
4. Restart application

---

## Advanced: Using GitHub API in Your App

### In main.py (FastAPI)

```python
from github import Github
from config import get_config

config = get_config()

@app.get("/github/repos")
async def list_github_repos():
    """List repositories from GitHub"""
    if not config.github.is_configured():
        raise HTTPException(status_code=400, detail="GitHub not configured")
    
    try:
        g = Github(config.github.api_token)
        user = g.get_user(config.github.owner)
        repos = []
        
        for repo in user.get_repos():
            repos.append({
                "name": repo.name,
                "url": repo.html_url,
                "stars": repo.stargazers_count,
                "language": repo.language
            })
        
        return {"repos": repos}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
```

### Using PyGithub Library

```bash
pip install PyGithub
```

Then in your code:

```python
from github import Github

g = Github(access_token)
user = g.get_user()
print(f"Hello {user.name}!")
```

---

## GitHub API Documentation

- **GitHub REST API**: https://docs.github.com/rest
- **PyGithub Library**: https://pygithub.readthedocs.io
- **Personal Access Tokens**: https://docs.github.com/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens

---

## Quick Reference

### Generate Token
1. Go to https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Name: `Trading Platform API`
4. Select scopes: `repo`, `read:user`, `user:email`
5. Click "Generate token"
6. Copy token immediately

### Add to .env
```env
GITHUB_API_TOKEN=ghp_your_token_here
GITHUB_OWNER=your-username
GITHUB_REPO=your-repo-name
```

### Verify
```bash
python verify_system.py
```

### Use in Code
```python
from config import get_config
from github import Github

config = get_config()
g = Github(config.github.api_token)
# Now use g to interact with GitHub API
```

---

## Next Steps

1. ✅ Create personal access token
2. ✅ Add to .env file
3. ✅ Run verification
4. ✅ Test with simple script
5. ✅ Integrate into your application
6. ✅ Set up token rotation schedule

**Your GitHub integration is ready!** 🚀

