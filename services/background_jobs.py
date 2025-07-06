"""
Background Job Manager for MessageHub
Handles launching, monitoring, and managing background campaign processes
"""

import os
import sys
import subprocess
import sqlite3
import time
import psutil
from datetime import datetime
from typing import Optional, List, Dict
import json

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from features.common import DB_FILE

class BackgroundJobManager:
    def __init__(self):
        self.db_path = DB_FILE
        self.logs_dir = os.path.join(project_root, 'logs')
        self.pids_dir = os.path.join(project_root, 'pids')
        
        # Ensure directories exist
        os.makedirs(self.logs_dir, exist_ok=True)
        os.makedirs(self.pids_dir, exist_ok=True)
    
    def start_campaign_background(self, campaign_id: int, campaign_type: str = 'email') -> bool:
        """Start a campaign in background mode"""
        try:
            # Check if campaign is already running
            if self.is_campaign_running(campaign_id, campaign_type):
                return False
            
            # Prepare command
            processor_script = os.path.join(project_root, 'campaign_processor.py')
            pid_file = os.path.join(self.pids_dir, f"{campaign_type}_{campaign_id}.pid")
            
            # Use Python executable from current environment
            python_exe = sys.executable
            
            cmd = [
                python_exe, processor_script,
                str(campaign_id),
                '--type', campaign_type,
                '--pid-file', pid_file
            ]
            
            # Start background process
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                cwd=project_root
            )
            
            # Record job in database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO background_jobs (campaign_id, campaign_type, status, pid, started_at)
                VALUES (?, ?, 'running', ?, ?)
            """, (campaign_id, campaign_type, process.pid, datetime.now().isoformat()))
            conn.commit()
            conn.close()
            
            return True
            
        except Exception as e:
            print(f"Failed to start background campaign {campaign_id}: {e}")
            return False
    
    def is_campaign_running(self, campaign_id: int, campaign_type: str = 'email') -> bool:
        """Check if a campaign is currently running in background"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT pid FROM background_jobs 
                WHERE campaign_id = ? AND campaign_type = ? AND status = 'running'
                ORDER BY started_at DESC LIMIT 1
            """, (campaign_id, campaign_type))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                pid = result[0]
                # Check if process is actually running
                try:
                    process = psutil.Process(pid)
                    return process.is_running()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    # Process no longer exists, update database
                    self._mark_job_completed(campaign_id, campaign_type, 'stopped', 'Process not found')
                    return False
            
            return False
            
        except Exception:
            return False
    
    def stop_campaign(self, campaign_id: int, campaign_type: str = 'email') -> bool:
        """Stop a running background campaign"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT pid FROM background_jobs 
                WHERE campaign_id = ? AND campaign_type = ? AND status = 'running'
                ORDER BY started_at DESC LIMIT 1
            """, (campaign_id, campaign_type))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                pid = result[0]
                try:
                    process = psutil.Process(pid)
                    process.terminate()
                    
                    # Wait for graceful shutdown
                    try:
                        process.wait(timeout=10)
                    except psutil.TimeoutExpired:
                        process.kill()
                    
                    self._mark_job_completed(campaign_id, campaign_type, 'stopped', 'Stopped by user')
                    return True
                    
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    self._mark_job_completed(campaign_id, campaign_type, 'stopped', 'Process not found')
                    return True
            
            return False
            
        except Exception as e:
            print(f"Failed to stop campaign {campaign_id}: {e}")
            return False
    
    def get_campaign_status(self, campaign_id: int, campaign_type: str = 'email') -> Dict:
        """Get the current status of a campaign"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get campaign status from campaign table
            table_name = f"{campaign_type}_campaigns"
            cursor.execute(f"""
                SELECT status, last_updated, processing_details
                FROM {table_name} WHERE id = ?
            """, (campaign_id,))
            
            campaign_result = cursor.fetchone()
            
            # Get background job status
            cursor.execute("""
                SELECT status, pid, started_at, completed_at, error_message
                FROM background_jobs 
                WHERE campaign_id = ? AND campaign_type = ?
                ORDER BY started_at DESC LIMIT 1
            """, (campaign_id, campaign_type))
            
            job_result = cursor.fetchone()
            conn.close()
            
            status = {
                'campaign_status': campaign_result[0] if campaign_result else 'unknown',
                'last_updated': campaign_result[1] if campaign_result else None,
                'processing_details': campaign_result[2] if campaign_result else None,
                'background_job_status': None,
                'pid': None,
                'is_running': False,
                'started_at': None,
                'completed_at': None,
                'error_message': None
            }
            
            if job_result:
                status.update({
                    'background_job_status': job_result[0],
                    'pid': job_result[1],
                    'started_at': job_result[2],
                    'completed_at': job_result[3],
                    'error_message': job_result[4]
                })
                
                # Check if process is actually running
                if job_result[1] and job_result[0] == 'running':
                    try:
                        process = psutil.Process(job_result[1])
                        status['is_running'] = process.is_running()
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        status['is_running'] = False
            
            return status
            
        except Exception as e:
            print(f"Failed to get campaign status: {e}")
            return {'campaign_status': 'error', 'is_running': False}
    
    def get_running_campaigns(self) -> List[Dict]:
        """Get all currently running background campaigns"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT campaign_id, campaign_type, pid, started_at
                FROM background_jobs 
                WHERE status = 'running'
                ORDER BY started_at DESC
            """)
            
            results = cursor.fetchall()
            conn.close()
            
            running_campaigns = []
            for campaign_id, campaign_type, pid, started_at in results:
                # Verify process is actually running
                try:
                    process = psutil.Process(pid)
                    if process.is_running():
                        running_campaigns.append({
                            'campaign_id': campaign_id,
                            'campaign_type': campaign_type,
                            'pid': pid,
                            'started_at': started_at
                        })
                    else:
                        # Mark as stopped if process is not running
                        self._mark_job_completed(campaign_id, campaign_type, 'stopped', 'Process not found')
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    self._mark_job_completed(campaign_id, campaign_type, 'stopped', 'Process not found')
            
            return running_campaigns
            
        except Exception as e:
            print(f"Failed to get running campaigns: {e}")
            return []
    
    def cleanup_completed_jobs(self, older_than_days: int = 7):
        """Clean up completed background jobs older than specified days"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM background_jobs 
                WHERE status IN ('completed', 'failed', 'stopped') 
                AND datetime(completed_at) < datetime('now', '-{} days')
            """.format(older_than_days))
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Failed to cleanup completed jobs: {e}")
    
    def _mark_job_completed(self, campaign_id: int, campaign_type: str, status: str, error_message: str = None):
        """Mark a background job as completed"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE background_jobs 
                SET status = ?, completed_at = ?, error_message = ?
                WHERE campaign_id = ? AND campaign_type = ? AND status = 'running'
            """, (status, datetime.now().isoformat(), error_message, campaign_id, campaign_type))
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Failed to mark job completed: {e}")

# Singleton instance
_job_manager = None

def get_job_manager() -> BackgroundJobManager:
    """Get the singleton background job manager instance"""
    global _job_manager
    if _job_manager is None:
        _job_manager = BackgroundJobManager()
    return _job_manager
