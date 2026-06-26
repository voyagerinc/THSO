# Excel Master Exporter - Version Management & Deployment Guide

## 📋 Overview

The enhanced Excel Master Exporter includes automatic version management, Git integration, and Streamlit service controls. Every change to the application is tracked, versioned, and logged.

---

## 🔢 Version System

### Version Format: `MAJOR.MINOR.PATCH.BUILD`

Example: `5.2.1.45`

- **MAJOR** (5): Major feature releases
- **MINOR** (2): Auto-increments on code changes
- **PATCH** (1): Auto-increments on config/template changes
- **BUILD** (45): Increments on every run

### Auto-Version Increment Logic

The application automatically detects changes in three areas:

1. **app.py** (Code Changes)
   - Triggers: MINOR increment + PATCH reset
   - Example: `5.0.0.1` → `5.1.0.1`
   - Changelog Type: `code_update`

2. **sheet_templates.json** (Template Changes)
   - Triggers: PATCH increment
   - Example: `5.1.0.5` → `5.1.1.1`
   - Changelog Type: `template_update`

3. **custom_templates.json** (Custom Config Changes)
   - Triggers: PATCH increment
   - Example: `5.1.1.5` → `5.1.2.1`
   - Changelog Type: `custom_template_update`

### File Hash Tracking

The system uses SHA256 hashing to detect changes:

```json
{
  "app_hash": "abc123...",           # Hash of app.py
  "templates_hash": "def456...",      # Hash of sheet_templates.json
  "config_hash": "ghi789..."          # Hash of custom_templates.json
}
```

If any file's hash differs from the stored hash, the version increments.

---

## 📁 Files Generated

### 1. `version.json`
Stores complete version information:

```json
{
  "major": 5,
  "minor": 0,
  "patch": 0,
  "build": 1,
  "created": "2024-06-12T10:00:00",
  "last_modified": "2024-06-12T10:00:00",
  "app_hash": "abc123def456",
  "config_hash": null,
  "templates_hash": null
}
```

### 2. `changelog.json`
Chronological log of all changes (max 100 entries):

```json
[
  {
    "timestamp": "2024-06-12T14:30:00",
    "type": "code_update",
    "description": "Auto-version bump: App code modified",
    "details": "",
    "version": "v5.1.0.1",
    "user": "system"
  },
  {
    "timestamp": "2024-06-12T14:00:00",
    "type": "git_pull_restart",
    "description": "Git pull + Streamlit restart",
    "details": "Full deployment cycle completed",
    "version": "v5.0.0.42",
    "user": "system"
  }
]
```

### 3. `streamlit.log`
Application logs (created by service manager)

---

## 🚀 Deployment Operations

### Admin Panel Location
Access via **🛠️ Admin & Deploy** tab (requires login)

### Operation 1: Git Pull + Streamlit Restart
**Button:** `🔄 Git Pull + Streamlit Restart`

**What it does:**
1. ✅ Fetches latest changes from GitHub
2. ✅ Pulls remote branch to local
3. ✅ Triggers Streamlit application restart
4. ✅ Logs as `git_pull_restart` in changelog

**Use case:** Deploy latest code from main branch with zero downtime

**Progress indicators:**
- 20%: Git fetch initiated
- 60%: Code pulled successfully
- 100%: Application restarted

---

### Operation 2: Git Pull Only
**Button:** `📥 Git Pull Only`

**What it does:**
1. ✅ Fetches and pulls latest code
2. ✅ Does NOT restart application
3. ✅ Logs as `git_pull` in changelog

**Use case:** Update code without disrupting current session

---

### Operation 3: Streamlit Restart Only
**Button:** `🔁 Restart Streamlit Only`

**What it does:**
1. ✅ Restarts the running Streamlit process
2. ✅ Logs as `restart` in changelog

**Use case:** Clear session state, fix issues without pulling code

---

### Operation 4: Push to GitHub
**Input:** Commit message text

**What it does:**
1. ✅ Stages all changes (`git add .`)
2. ✅ Creates commit with custom message
3. ✅ Pushes to remote branch
4. ✅ Logs as `git_push` in changelog

**Use case:** Backup configuration changes to Git

---

## 📊 Version Display

### In-App Display (Collapsible Header)
Shows on every page after login:
```
ℹ️ Version 5.2.1 | Build 45
  ├─ Version: 5.2.1
  ├─ Build: 45
  ├─ Last Modified: 12 Jun 24
  ├─ Git Commit: a1b2c3d4
  ├─ Recent Changes (3 most recent)
  └─ Repository Status (Branch, Commit)
```

### In Admin Panel
**Version Information Card:**
- Version: `v5.2.1.45`
- Created: Full timestamp
- Last Modified: Full timestamp
- Branch: Current Git branch
- Commit: Current commit hash

**Changelog Display:**
- Shows last 10 entries
- Includes timestamp, type emoji, description
- Searchable by type

---

## 🔍 Tracking Changes

### What Gets Tracked?

| Action | Type | Increment | Example |
|--------|------|-----------|---------|
| Edit app.py | `code_update` | MINOR.PATCH=0 | 5.0.0 → 5.1.0 |
| Edit templates | `template_update` | PATCH | 5.1.0 → 5.1.1 |
| Edit custom configs | `custom_template_update` | PATCH | 5.1.1 → 5.1.2 |
| Git pull | `git_pull` | BUILD | 5.1.2.5 → 5.1.2.6 |
| Git push | `git_push` | BUILD | 5.1.2.6 → 5.1.2.7 |
| App restart | `restart` | BUILD | 5.1.2.7 → 5.1.2.8 |

### How to View Changes

1. **In-App UI:** Expand version badge on any page
2. **Changelog Panel:** View last 10 entries in Admin panel
3. **Command Line:** `cat changelog.json | jq`

---

## 💻 Service Management (Command Line)

### Using the Service Manager Script

```bash
chmod +x streamlit_service.sh

# Start the service
./streamlit_service.sh start

# Stop the service
./streamlit_service.sh stop

# Restart the service
./streamlit_service.sh restart

# Check status
./streamlit_service.sh status

# View logs (last 50 lines)
./streamlit_service.sh logs

# Follow logs in real-time
./streamlit_service.sh follow
```

### Expected Output

```
✅ Excel Master Exporter started successfully (PID: 12345)
ℹ️  Running on http://0.0.0.0:8501
ℹ️  Logs: /path/to/streamlit.log
```

### Configuration

Edit variables in `streamlit_service.sh`:

```bash
PORT=8501              # Port number
HOST=0.0.0.0          # Host address
LOG_FILE="..."        # Log file location
PID_FILE="..."        # PID file location
```

---

## 🔐 Security Notes

### Version File Integrity
- Version files are JSON (human-readable)
- Keep in version control for audit trail
- Backup regularly with code repository

### File Hash Validation
- Hashes detect unauthorized changes
- Cannot be spoofed (SHA256 cryptographic)
- Mismatch triggers automatic version bump

### Access Control
- Admin operations require login
- Default credentials: `admin` / `PaSSw0rd@1`
- Change credentials in app code before production

---

## 📚 Git Integration Best Practices

### Recommended Workflow

1. **Development** (Local)
   ```
   Edit app.py → Auto-version bump → Manual git commit
   ```

2. **Push to Repository**
   ```
   Use "Push to GitHub" in Admin panel
   ```

3. **Deploy Changes**
   ```
   Use "Git Pull + Restart" in Admin panel
   ```

### Git Status Indicators

- ✅ **Green**: Working directory is clean
- ⚠️ **Yellow**: N files have uncommitted changes

### Automatic Changelog

Every operation creates a changelog entry with:
- Exact timestamp (ISO 8601)
- Operation type (git_pull, restart, etc.)
- Version at time of operation
- Detailed description

---

## 🐛 Troubleshooting

### Version Not Incrementing?

1. Check `version.json` exists
2. Verify file hashes are being calculated
3. Check `changelog.json` for errors
4. Restart app with `streamlit run app.py`

### Git Commands Failing?

1. Ensure Git is installed: `git --version`
2. Check repository URL in code
3. Verify SSH/HTTPS credentials
4. Review logs: `./streamlit_service.sh logs`

### Streamlit Won't Restart?

1. Check process: `ps aux | grep streamlit`
2. View logs: `./streamlit_service.sh follow`
3. Force kill: `killall -9 streamlit`
4. Restart manually: `./streamlit_service.sh start`

---

## 📝 Examples

### Example Scenario 1: Update Code and Deploy

```
1. Edit app.py → Adds new feature
   ✓ Version: 5.0.0.15 → 5.1.0.1
   ✓ Changelog: "Auto-version bump: App code modified"

2. Click "Git Pull + Streamlit Restart"
   ✓ Code fetched from GitHub
   ✓ App restarts automatically
   ✓ Changelog: "Git pull + Streamlit restart"
   ✓ Version: 5.1.0.1 → 5.1.0.2

3. View Admin panel
   ✓ Shows Version: v5.1.0.2
   ✓ Shows 2 latest entries in changelog
   ✓ Shows current commit hash
```

### Example Scenario 2: Update Templates

```
1. Edit "All Records" template (in Templates tab)
   ✓ Change filter settings
   ✓ Click "Save Changes"
   ✓ Version: 5.1.0.2 → 5.1.1.1
   ✓ Changelog: "Sheet templates updated"

2. Check version badge
   ✓ Shows new version 5.1.1
   ✓ Shows timestamp of last change
   ✓ Shows recent changelog entries
```

### Example Scenario 3: Custom Configuration

```
1. Create custom template (in Custom tab)
   ✓ Name: "High Value Orders"
   ✓ Click "Save Custom Template"
   ✓ Version: 5.1.1.5 → 5.1.2.1
   ✓ Changelog: "Custom templates updated"

2. Push to GitHub
   ✓ Enter message: "Added High Value Orders template"
   ✓ Click "Push to GitHub"
   ✓ Changelog: "Pushed changes to GitHub"
```

---

## 🔗 Environment Variables

Set these for custom configuration:

```bash
export PORT=8501              # Streamlit port
export HOST=0.0.0.0          # Streamlit host
export GITHUB_BRANCH=main      # Git branch to track
export LOG_LEVEL=info          # Streamlit log level
```

---

## 📞 Support

For issues or questions:

1. Check changelog for recent changes
2. Review logs: `./streamlit_service.sh logs`
3. Verify Git connectivity: `git status`
4. Restart service: `./streamlit_service.sh restart`

---

**Last Updated:** June 2024
**Version System:** v1.0
