# Quick Start Guide - Excel Master Exporter v5.0+

## 🚀 Initial Setup

### 1. Prerequisites
```bash
# Install dependencies
pip install streamlit pandas openpyxl numpy

# Make service script executable
chmod +x streamlit_service.sh
```

### 2. First Run
```bash
# Option A: Direct Streamlit
streamlit run app.py

# Option B: Using service manager
./streamlit_service.sh start

# Option C: With custom port
streamlit run app.py --server.port 8502
```

### 3. First Login
```
Username: admin
Password: PaSSw0rd@1
```

⚠️ **Change these credentials immediately in production!**

---

## 📊 Version Badge Explained

When you log in, you'll see a collapsible version section:

```
ℹ️ Version 5.0.0 | Build 1
│
├─ Version: 5.0.0         ← Format: MAJOR.MINOR.PATCH
├─ Build: 1              ← Increments every run
├─ Last Modified: 12 Jun ← Timestamp of last change
├─ Git Commit: a1b2c3d4  ← Current Git commit
└─ Recent Changes        ← Shows last 3 changes
```

---

## 🔄 Common Workflows

### Workflow 1: Making Code Changes

```
1. Edit app.py
   └─ Add new feature or fix bug

2. Log into app → Check version badge
   └─ Version auto-incremented? 
   └─ Example: 5.0.0 → 5.1.0

3. Go to 🛠️ Admin & Deploy tab
   └─ Click "📤 Push to GitHub"
   └─ Enter message: "Added new feature"

4. Click "🔄 Git Pull + Streamlit Restart"
   └─ Code deployed to production
   └─ Version incremented again: 5.1.0 → 5.1.0.2
```

### Workflow 2: Template Configuration

```
1. Go to ⚙️ Templates tab
   └─ Edit "All Records" template

2. Change filter settings → Click "Save Changes"
   └─ Version auto-incremented
   └─ Example: 5.1.0.2 → 5.1.1.1

3. Check Admin panel
   └─ See "Sheet templates updated" in changelog
   └─ Timestamp shows exactly when changed
```

### Workflow 3: Custom Templates

```
1. Go to 📋 Custom tab
   └─ Create new custom template

2. Name it (e.g., "VIP Orders") → Save
   └─ Version incremented: 5.1.1.5 → 5.1.2.1
   └─ Logged as "custom_template_update"

3. Next time app runs
   └─ Build number increments: 5.1.2.1 → 5.1.2.2
```

### Workflow 4: Emergency Restart

```
1. Something's broken → Go to 🛠️ Admin & Deploy
   
2. Click "🔁 Restart Streamlit Only"
   └─ App restarts without pulling code
   └─ Clears session state
   
3. Version increments: 5.1.2.5 → 5.1.2.6
   └─ Logged as "restart"
```

---

## 📁 Important Files

```
project/
├── app.py                          ← Main application
├── version.json                    ← Version info (auto-generated)
├── changelog.json                  ← Change log (auto-generated)
├── streamlit_service.sh            ← Service manager
├── streamlit.log                   ← Application logs (auto-generated)
├── streamlit.pid                   ← Process ID (auto-generated)
├── sheet_templates.json            ← Template config
├── custom_templates.json           ← Custom config
└── VERSION_MANAGEMENT_GUIDE.md     ← Full documentation
```

---

## 🔢 Understanding Version Numbers

| Version | Meaning | Cause |
|---------|---------|-------|
| 5.0.0.1 | Initial | First run |
| 5.1.0.1 | Code changed | app.py modified |
| 5.1.1.1 | Template changed | sheet_templates.json modified |
| 5.1.1.2 | Just rebuilt | Any run without file changes |
| 5.1.1.3 | Another run | Streamlit rerun |
| 5.1.2.1 | Custom config changed | custom_templates.json modified |

### Quick Decision Tree

```
Your change was to:
├─ app.py → MINOR increments (5.0.0 → 5.1.0)
├─ Templates → PATCH increments (5.1.0 → 5.1.1)
├─ Custom config → PATCH increments (5.1.1 → 5.1.2)
└─ Nothing → Just BUILD increments (5.1.2.1 → 5.1.2.2)
```

---

## 🛠️ Admin Panel Tour

### Left Column: Deployment Operations

**🔄 Git Pull + Streamlit Restart**
- Most common operation
- Pulls latest code + restarts app
- Perfect for production deployments

**📥 Git Pull Only**
- Update code without restarting
- Useful if users are in middle of work

**🔁 Restart Streamlit Only**
- Just restart the app
- Don't pull new code
- For emergency fixes

**📤 Push to GitHub**
- Save your config changes
- Back up templates
- Create audit trail

### Right Column: Application Status

**Version Information**
- Shows current version: 5.0.0.1
- Shows created date
- Shows last modified date
- Shows Git branch & commit

**Git Status**
- ✅ Clean (no uncommitted changes)
- ⚠️ Changes pending (N files modified)

**Changelog (Last 10)**
- Recent 10 changes
- Type emoji (📝, ⚙️, 📥, 🔁, etc.)
- Timestamp for each

---

## 📊 Monitoring Version Changes

### Option 1: In-App (Easiest)
1. Expand version badge after login
2. Scroll down in Admin panel
3. See all recent changes with timestamps

### Option 2: Command Line
```bash
# View current version
cat version.json | jq '.major, .minor, .patch, .build'

# View recent changes
cat changelog.json | jq '.[0:5]'

# View specific type of changes
cat changelog.json | jq '.[] | select(.type=="code_update")'

# Count total changes by type
cat changelog.json | jq 'group_by(.type) | map({type: .[0].type, count: length})'
```

### Option 3: Git Integration
```bash
# See what changed in app.py
git diff app.py

# See history of changes
git log --oneline -10

# See file changes
git status
```

---

## 🚨 Common Issues & Solutions

### Issue: Version not incrementing
**Solution:** 
1. Restart app: `streamlit run app.py`
2. Check version.json exists
3. Verify file permissions

### Issue: Git commands failing
**Solution:**
1. Check Git installed: `git --version`
2. Verify credentials configured
3. Test: `git status`
4. Check logs: `./streamlit_service.sh logs`

### Issue: Can't find Admin tab
**Solution:**
1. Make sure you're logged in
2. Scroll right if on mobile
3. Check that tabs rendered correctly

### Issue: Changes not showing in changelog
**Solution:**
1. Refresh browser: `Ctrl+Shift+R`
2. Check changelog.json exists
3. Verify write permissions

---

## 🔐 Production Checklist

Before deploying to production:

- [ ] Change admin password in app.py
- [ ] Set up Git repository
- [ ] Configure GitHub URL in GITHUB_CONFIG
- [ ] Test "Git Pull + Restart" cycle
- [ ] Review version.json and changelog.json
- [ ] Set up regular backups
- [ ] Test all deployment operations
- [ ] Configure environment variables
- [ ] Set up systemd service (optional, see systemd-service.txt)
- [ ] Enable HTTPS if internet-facing

---

## 📱 Mobile Access

Version management works on mobile too:

1. Same login screen
2. Version badge collapses more (smaller screen)
3. Admin panel tabs stack vertically
4. All operations work identically

---

## 🎯 Key Takeaways

1. **Auto-Versioning**: Every change triggers automatic version bump
2. **Change Tracking**: All changes logged with timestamp & type
3. **One-Click Deploy**: "Git Pull + Restart" does full deployment
4. **Easy Monitoring**: See version changes everywhere in UI
5. **Audit Trail**: Changelog keeps 100 most recent changes

---

## 📚 Next Steps

1. Read full docs: `VERSION_MANAGEMENT_GUIDE.md`
2. Try each operation in Admin panel
3. Make template change and watch version increment
4. Push changes to GitHub
5. Deploy with Git Pull + Restart

**Good luck! 🚀**
