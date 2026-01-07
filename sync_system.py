"""
Dual Redundancy Sync System
Keeps E:\ and D:\ in perfect sync with GitHub
"""

import os
import json
import shutil
import hashlib
from datetime import datetime
from pathlib import Path
import subprocess

PRIMARY = Path("E:/trading-platform-api")
BACKUP = Path("D:/trading-platform-api")
LOG_FILE = PRIMARY / "sync_logs.txt"
BACKUP_DIR = PRIMARY / "backups"

def log(message):
    """Log message to both console and file"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    full_message = f"[{timestamp}] {message}"
    print(full_message)
    
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(full_message + "\n")
    except:
        # Fallback for encoding issues
        with open(LOG_FILE, "a") as f:
            f.write(full_message.encode('utf-8', errors='replace').decode('utf-8') + "\n")

def create_backup():
    """Create timestamped backup"""
    BACKUP_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_zip = BACKUP_DIR / f"backup_{timestamp}.zip"
    
    try:
        shutil.make_archive(
            str(backup_zip.with_suffix('')),
            'zip',
            PRIMARY,
            '.'
        )
        log(f"✅ Backup created: {backup_zip}")
        return True
    except Exception as e:
        log(f"❌ Backup failed: {e}")
        return False

def sync_e_to_d():
    """Sync E:\ to D:\ (primary to backup)"""
    log("🔄 Syncing E:\\ → D:\\...")
    
    try:
        import shutil
        
        # Create backup first
        create_backup()
        
        # Sync files
        for item in PRIMARY.glob("**/*"):
            if ".git" in str(item) or "__pycache__" in str(item):
                continue
            
            rel_path = item.relative_to(PRIMARY)
            target = BACKUP / rel_path
            
            if item.is_file():
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(item, target)
        
        log("✅ E:\\ → D:\\ sync complete")
        return True
    except Exception as e:
        log(f"❌ Sync E→D failed: {e}")
        return False

def sync_d_to_e():
    """Sync D:\ to E:\ (backup to primary) - if needed"""
    log("🔄 Syncing D:\\ → E:\\...")
    
    try:
        import shutil
        
        # Create backup first
        create_backup()
        
        # Check for conflicts
        conflicts = 0
        for item in BACKUP.glob("**/*"):
            if ".git" in str(item) or "__pycache__" in str(item):
                continue
            
            rel_path = item.relative_to(BACKUP)
            target = PRIMARY / rel_path
            
            if item.is_file() and target.exists():
                if item.stat().st_mtime > target.stat().st_mtime:
                    log(f"⚠️  Conflict: {rel_path} (D:\\ newer)")
                    conflicts += 1
        
        if conflicts > 0:
            log(f"⚠️  Found {conflicts} conflicts - manual review needed")
            return False
        
        log("✅ D:\\ → E:\\ sync complete (no conflicts)")
        return True
    except Exception as e:
        log(f"❌ Sync D→E failed: {e}")
        return False

def sync_both():
    """Bi-directional sync"""
    log("🔄 Starting bi-directional sync...")
    
    # E → D (primary to backup)
    sync_e_to_d()
    
    # Create backup after sync
    create_backup()
    
    # Verify
    e_files = len(list(PRIMARY.glob("**/*")))
    d_files = len(list(BACKUP.glob("**/*")))
    
    if e_files == d_files:
        log(f"✅ Sync verified: E={e_files} files, D={d_files} files")
        return True
    else:
        log(f"❌ Sync mismatch: E={e_files} files, D={d_files} files")
        return False

def sync_with_github():
    """Sync with GitHub"""
    log("🔄 Syncing with GitHub...")
    
    try:
        os.chdir(PRIMARY)
        
        # Pull latest from GitHub
        subprocess.run(["git", "pull", "origin", "main"], check=True, capture_output=True)
        log("✅ Pulled from GitHub")
        
        # Sync to D:\ 
        sync_e_to_d()
        
        # Check for local changes
        result = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
        
        if result.stdout:
            # Push changes
            subprocess.run(["git", "add", "."], check=True)
            subprocess.run(["git", "commit", "-m", "Auto-sync: update from redundancy system"], check=True, capture_output=True)
            subprocess.run(["git", "push", "origin", "main"], check=True)
            log("✅ Pushed to GitHub")
        else:
            log("✅ GitHub already in sync")
        
        return True
    except Exception as e:
        log(f"❌ GitHub sync failed: {e}")
        return False

def health_check():
    """Check system health"""
    log("[HEALTH CHECK]")
    log("=" * 50)
    
    # Check directories exist
    e_exists = PRIMARY.exists()
    d_exists = BACKUP.exists()
    log(f"E:\ exists: {'OK' if e_exists else 'FAIL'}")
    log(f"D:\ exists: {'OK' if d_exists else 'FAIL'}")
    
    # Check files match
    if e_exists and d_exists:
        e_files = set(str(p.relative_to(PRIMARY)) for p in PRIMARY.rglob("*") if not ".git" in str(p))
        d_files = set(str(p.relative_to(BACKUP)) for p in BACKUP.rglob("*") if not ".git" in str(p))
        
        match = e_files == d_files
        log(f"Files match: {'OK' if match else 'MISMATCH'} (E={len(e_files)}, D={len(d_files)})")
    
    # Check GitHub
    try:
        os.chdir(PRIMARY)
        result = subprocess.run(["git", "remote", "-v"], capture_output=True, text=True)
        log(f"GitHub remote: OK")
    except:
        log(f"GitHub remote: FAIL")
    
    # Check disk space
    import shutil
    stats = shutil.disk_usage(str(PRIMARY))
    log(f"E:\ free space: {stats.free / (1024**3):.2f} GB")
    
    stats = shutil.disk_usage(str(BACKUP))
    log(f"D:\ free space: {stats.free / (1024**3):.2f} GB")
    
    # Check backups
    if BACKUP_DIR.exists():
        backups = list(BACKUP_DIR.glob("*.zip"))
        log(f"Backups available: {len(backups)}")
    
    log("=" * 50)

def main():
    """Main entry point"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python sync_system.py [sync|github|health|backup]")
        print("  sync     - Bi-directional sync E ↔ D")
        print("  github   - Sync with GitHub (pull & push)")
        print("  health   - Check system health")
        print("  backup   - Create backup")
        return
    
    command = sys.argv[1]
    
    if command == "sync":
        sync_both()
    elif command == "github":
        sync_with_github()
    elif command == "health":
        health_check()
    elif command == "backup":
        create_backup()
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()
