# 📤 GitHub Upload Guide

Step-by-step instructions to upload your project to GitHub.

## Prerequisites

- Git installed
- GitHub account
- Repository already initialized locally ✓

## Step 1: Create GitHub Repository

1. Go to [GitHub.com](https://github.com)
2. Click the `+` icon (top right) → "New repository"
3. Fill in details:
   - **Repository name**: `distributed-file-sharing` (or your choice)
   - **Description**: "Fault-tolerant distributed file sharing system with primary-backup replication and automatic failover"
   - **Visibility**: Public (recommended for CV/portfolio)
   - **DON'T** initialize with README (we already have one)
4. Click "Create repository"

## Step 2: Connect Local Repository to GitHub

```bash
cd "d:\Distributed Computing"

# Add remote origin (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/distributed-file-sharing.git

# Verify remote was added
git remote -v
```

## Step 3: Push to GitHub

```bash
# Rename branch to 'main' (GitHub default)
git branch -M main

# Push to GitHub
git push -u origin main
```

### If you encounter authentication issues:

**Option 1: Personal Access Token (Recommended)**
1. Go to GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Click "Generate new token (classic)"
3. Select scopes: `repo` (all sub-options)
4. Copy the token
5. When pushing, use token as password:
   ```
   Username: YOUR_USERNAME
   Password: ghp_YourTokenHere
   ```

**Option 2: SSH (Advanced)**
```bash
# Generate SSH key
ssh-keygen -t ed25519 -C "your_email@example.com"

# Add to GitHub: Settings → SSH and GPG keys → New SSH key
# Copy from: cat ~/.ssh/id_ed25519.pub

# Use SSH remote instead
git remote set-url origin git@github.com:YOUR_USERNAME/distributed-file-sharing.git
git push -u origin main
```

## Step 4: Verify Upload

1. Go to your repository URL: `https://github.com/YOUR_USERNAME/distributed-file-sharing`
2. Verify all files are uploaded
3. README.md should display automatically

## Step 5: Customize Repository

### Add Topics
1. Go to repository → Click ⚙️ next to "About"
2. Add topics:
   - `distributed-systems`
   - `file-sharing`
   - `python`
   - `fault-tolerance`
   - `socket-programming`
   - `replication`
   - `peer-to-peer`

### Update README
Replace placeholders in README.md:
```yaml
- GitHub: [@yourusername] → [@YOUR_ACTUAL_USERNAME]
- LinkedIn: [Your Name] → [YOUR_NAME]
- Email: your.email@example.com → YOUR_EMAIL
```

```bash
# Commit changes
git add README.md
git commit -m "Update author information"
git push
```

## Step 6: Enable GitHub Pages (Optional)

1. Repository → Settings → Pages
2. Source: Deploy from branch → `main`
3. Click Save
4. Your project will be available at: `https://YOUR_USERNAME.github.io/distributed-file-sharing`

## Step 7: Add Badges (Optional but Professional)

Add to top of README.md:
```markdown
[![GitHub stars](https://img.shields.io/github/stars/YOUR_USERNAME/distributed-file-sharing)](https://github.com/YOUR_USERNAME/distributed-file-sharing/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/YOUR_USERNAME/distributed-file-sharing)](https://github.com/YOUR_USERNAME/distributed-file-sharing/network)
[![GitHub issues](https://img.shields.io/github/issues/YOUR_USERNAME/distributed-file-sharing)](https://github.com/YOUR_USERNAME/distributed-file-sharing/issues)
```

## Future Updates

When you make changes:
```bash
# Stage changes
git add .

# Commit with descriptive message
git commit -m "Add feature: XYZ"

# Push to GitHub
git push
```

## Useful Git Commands

```bash
# Check status
git status

# View commit history
git log --oneline

# Create a new branch
git checkout -b feature-name

# Switch branches
git checkout main

# Undo last commit (keep changes)
git reset --soft HEAD~1

# Undo last commit (discard changes)
git reset --hard HEAD~1
```

## Portfolio Presentation Tips

### For Your CV
```
Distributed File Sharing System | Python, Sockets, SQLite
GitHub: github.com/YOUR_USERNAME/distributed-file-sharing

• Architected fault-tolerant distributed system with primary-backup 
  replication and automatic failover
• Implemented SHA256 integrity verification for chunked file transfers
• Designed configuration-driven deployment with YAML
• Built persistent storage layer using SQLite
```

### For Interviews
1. Show the **architecture diagram** in README
2. Demo **automatic failover** live
3. Explain **design decisions** (why checksums? why SQLite?)
4. Walk through **error handling** implementation
5. Discuss **scalability** considerations

## Troubleshooting

### "fatal: remote origin already exists"
```bash
git remote remove origin
git remote add origin https://github.com/YOUR_USERNAME/repo-name.git
```

### "refusing to merge unrelated histories"
```bash
git pull origin main --allow-unrelated-histories
```

### Large files error
```bash
# Remove from git but keep locally
git rm --cached filename
echo "filename" >> .gitignore
git add .gitignore
git commit -m "Remove large file"
git push
```

## Done! 🎉

Your project is now on GitHub and ready for:
- ✅ Sharing in job applications
- ✅ Adding to LinkedIn projects
- ✅ Including in your portfolio
- ✅ Demonstrating in interviews

**Remember to star your own repository to show activity!** ⭐

---

Need help? Open an issue on GitHub or refer to [GitHub Docs](https://docs.github.com).
