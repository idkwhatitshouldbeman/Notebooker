"""
Automated Backup System for Notebooker
Provides consistent backups and version control
"""

import os
import json
import shutil
import zipfile
from datetime import datetime, timedelta
from pathlib import Path
import logging
import schedule
import time
from typing import Dict, List, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BackupManager:
    """Manages automated backups for the EN Writer system"""
    
    def __init__(self, base_dir: str = ".", backup_dir: str = "backups"):
        self.base_dir = Path(base_dir)
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)
        self.config_file = self.backup_dir / "backup_config.json"
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load backup configuration"""
        default_config = {
            "auto_backup_enabled": True,
            "backup_interval_minutes": 30,
            "max_backups": 10,
            "backup_retention_days": 7,
            "include_files": [
                "en_files/",
                "planning_sheet.json",
                "activity_log.json",
                "images/",
                "*.py",
                "*.txt",
                "*.md"
            ],
            "exclude_files": [
                "__pycache__/",
                "*.pyc",
                ".git/",
                "node_modules/",
                "*.log"
            ]
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # Merge with defaults for any missing keys
                    for key, value in default_config.items():
                        if key not in config:
                            config[key] = value
                    return config
            except Exception as e:
                logger.error(f"Error loading backup config: {e}")
                return default_config
        else:
            self._save_config(default_config)
            return default_config
    
    def _save_config(self, config: Dict[str, Any]):
        """Save backup configuration"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving backup config: {e}")
    
    def create_backup(self, backup_name: str = None) -> str:
        """Create a new backup"""
        try:
            if not backup_name:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_name = f"backup_{timestamp}"
            
            backup_path = self.backup_dir / f"{backup_name}.zip"
            
            # Create zip file
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                self._add_files_to_zip(zipf)
            
            # Create metadata file
            metadata = {
                "backup_name": backup_name,
                "created_at": datetime.now().isoformat(),
                "file_count": self._count_files(),
                "total_size": self._calculate_total_size(),
                "config": self.config
            }
            
            metadata_file = self.backup_dir / f"{backup_name}_metadata.json"
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Backup created: {backup_name}")
            return str(backup_path)
            
        except Exception as e:
            logger.error(f"Error creating backup: {e}")
            return None
    
    def _add_files_to_zip(self, zipf: zipfile.ZipFile):
        """Add files to zip archive based on configuration"""
        include_patterns = self.config.get("include_files", [])
        exclude_patterns = self.config.get("exclude_files", [])
        
        for root, dirs, files in os.walk(self.base_dir):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if not self._should_exclude(d, exclude_patterns)]
            
            for file in files:
                file_path = Path(root) / file
                relative_path = file_path.relative_to(self.base_dir)
                
                # Check if file should be included
                if self._should_include(str(relative_path), include_patterns) and \
                   not self._should_exclude(str(relative_path), exclude_patterns):
                    zipf.write(file_path, relative_path)
    
    def _should_include(self, file_path: str, patterns: List[str]) -> bool:
        """Check if file should be included based on patterns"""
        import fnmatch
        
        for pattern in patterns:
            if fnmatch.fnmatch(file_path, pattern) or fnmatch.fnmatch(file_path, f"*/{pattern}"):
                return True
        return False
    
    def _should_exclude(self, file_path: str, patterns: List[str]) -> bool:
        """Check if file should be excluded based on patterns"""
        import fnmatch
        
        for pattern in patterns:
            if fnmatch.fnmatch(file_path, pattern) or fnmatch.fnmatch(file_path, f"*/{pattern}"):
                return True
        return False
    
    def _count_files(self) -> int:
        """Count total files to be backed up"""
        count = 0
        include_patterns = self.config.get("include_files", [])
        exclude_patterns = self.config.get("exclude_files", [])
        
        for root, dirs, files in os.walk(self.base_dir):
            dirs[:] = [d for d in dirs if not self._should_exclude(d, exclude_patterns)]
            
            for file in files:
                file_path = Path(root) / file
                relative_path = file_path.relative_to(self.base_dir)
                
                if self._should_include(str(relative_path), include_patterns) and \
                   not self._should_exclude(str(relative_path), exclude_patterns):
                    count += 1
        
        return count
    
    def _calculate_total_size(self) -> int:
        """Calculate total size of files to be backed up"""
        total_size = 0
        include_patterns = self.config.get("include_files", [])
        exclude_patterns = self.config.get("exclude_files", [])
        
        for root, dirs, files in os.walk(self.base_dir):
            dirs[:] = [d for d in dirs if not self._should_exclude(d, exclude_patterns)]
            
            for file in files:
                file_path = Path(root) / file
                relative_path = file_path.relative_to(self.base_dir)
                
                if self._should_include(str(relative_path), include_patterns) and \
                   not self._should_exclude(str(relative_path), exclude_patterns):
                    try:
                        total_size += file_path.stat().st_size
                    except OSError:
                        pass
        
        return total_size
    
    def list_backups(self) -> List[Dict[str, Any]]:
        """List all available backups"""
        backups = []
        
        for backup_file in self.backup_dir.glob("backup_*.zip"):
            backup_name = backup_file.stem
            metadata_file = self.backup_dir / f"{backup_name}_metadata.json"
            
            if metadata_file.exists():
                try:
                    with open(metadata_file, 'r', encoding='utf-8') as f:
                        metadata = json.load(f)
                    backups.append(metadata)
                except Exception as e:
                    logger.error(f"Error reading metadata for {backup_name}: {e}")
            else:
                # Create basic metadata from file info
                stat = backup_file.stat()
                backups.append({
                    "backup_name": backup_name,
                    "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                    "file_count": "Unknown",
                    "total_size": stat.st_size
                })
        
        # Sort by creation date (newest first)
        backups.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return backups
    
    def restore_backup(self, backup_name: str, restore_path: str = None) -> bool:
        """Restore from a backup"""
        try:
            backup_file = self.backup_dir / f"{backup_name}.zip"
            
            if not backup_file.exists():
                logger.error(f"Backup file not found: {backup_name}")
                return False
            
            if not restore_path:
                restore_path = self.base_dir
            else:
                restore_path = Path(restore_path)
                restore_path.mkdir(exist_ok=True)
            
            # Extract backup
            with zipfile.ZipFile(backup_file, 'r') as zipf:
                zipf.extractall(restore_path)
            
            logger.info(f"Backup restored: {backup_name} to {restore_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error restoring backup: {e}")
            return False
    
    def cleanup_old_backups(self):
        """Remove old backups based on retention policy"""
        try:
            max_backups = self.config.get("max_backups", 10)
            retention_days = self.config.get("backup_retention_days", 7)
            cutoff_date = datetime.now() - timedelta(days=retention_days)
            
            backups = self.list_backups()
            
            # Remove backups older than retention period
            for backup in backups:
                try:
                    created_at = datetime.fromisoformat(backup["created_at"])
                    if created_at < cutoff_date:
                        backup_name = backup["backup_name"]
                        self._remove_backup(backup_name)
                except Exception as e:
                    logger.error(f"Error processing backup {backup.get('backup_name', 'unknown')}: {e}")
            
            # Remove excess backups (keep only max_backups)
            backups = self.list_backups()
            if len(backups) > max_backups:
                for backup in backups[max_backups:]:
                    backup_name = backup["backup_name"]
                    self._remove_backup(backup_name)
            
            logger.info("Backup cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during backup cleanup: {e}")
    
    def _remove_backup(self, backup_name: str):
        """Remove a specific backup"""
        try:
            backup_file = self.backup_dir / f"{backup_name}.zip"
            metadata_file = self.backup_dir / f"{backup_name}_metadata.json"
            
            if backup_file.exists():
                backup_file.unlink()
            if metadata_file.exists():
                metadata_file.unlink()
            
            logger.info(f"Backup removed: {backup_name}")
            
        except Exception as e:
            logger.error(f"Error removing backup {backup_name}: {e}")
    
    def start_auto_backup(self):
        """Start automatic backup scheduling"""
        if not self.config.get("auto_backup_enabled", True):
            logger.info("Auto backup is disabled")
            return
        
        interval_minutes = self.config.get("backup_interval_minutes", 30)
        
        # Schedule backup
        schedule.every(interval_minutes).minutes.do(self._auto_backup_job)
        
        logger.info(f"Auto backup started - interval: {interval_minutes} minutes")
        
        # Run cleanup on startup
        self.cleanup_old_backups()
        
        # Keep running
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    def _auto_backup_job(self):
        """Automatic backup job"""
        try:
            backup_path = self.create_backup()
            if backup_path:
                logger.info(f"Auto backup completed: {backup_path}")
                # Run cleanup after each backup
                self.cleanup_old_backups()
        except Exception as e:
            logger.error(f"Auto backup failed: {e}")
    
    def get_backup_status(self) -> Dict[str, Any]:
        """Get current backup status"""
        backups = self.list_backups()
        
        return {
            "auto_backup_enabled": self.config.get("auto_backup_enabled", True),
            "backup_interval_minutes": self.config.get("backup_interval_minutes", 30),
            "max_backups": self.config.get("max_backups", 10),
            "retention_days": self.config.get("backup_retention_days", 7),
            "total_backups": len(backups),
            "latest_backup": backups[0] if backups else None,
            "backup_dir": str(self.backup_dir),
            "total_size": sum(backup.get("total_size", 0) for backup in backups)
        }


# Example usage
if __name__ == "__main__":
    # Create backup manager
    backup_manager = BackupManager()
    
    # Create a backup
    backup_path = backup_manager.create_backup("test_backup")
    print(f"Backup created: {backup_path}")
    
    # List backups
    backups = backup_manager.list_backups()
    print(f"Available backups: {len(backups)}")
    
    # Get status
    status = backup_manager.get_backup_status()
    print(f"Backup status: {status}")
    
    # Start auto backup (uncomment to run)
    # backup_manager.start_auto_backup()
