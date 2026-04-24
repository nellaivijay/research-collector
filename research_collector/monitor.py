"""Monitor mode for periodic research scheduling."""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from research_collector.config import Config
from research_collector.pipeline import Pipeline


class Monitor:
    """Monitor for scheduling periodic research."""
    
    def __init__(self, config: Config):
        """Initialize monitor."""
        self.config = config
        self.monitor_file = Path.home() / ".research-collector" / "monitors.json"
        self.monitor_file.parent.mkdir(parents=True, exist_ok=True)
        self.monitors = self._load_monitors()
    
    def _load_monitors(self) -> Dict:
        """Load monitor configurations from file."""
        if self.monitor_file.exists():
            with open(self.monitor_file, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_monitors(self) -> None:
        """Save monitor configurations to file."""
        with open(self.monitor_file, 'w') as f:
            json.dump(self.monitors, f, indent=2)
    
    def add_monitor(
        self,
        name: str,
        topic: str,
        interval_hours: int,
        sources: Optional[List[str]] = None,
        output_dir: Optional[str] = None
    ) -> str:
        """Add a new monitor.
        
        Args:
            name: Monitor name/ID
            topic: Research topic
            interval_hours: Check interval in hours
            sources: List of sources to use
            output_dir: Directory to save results
        
        Returns:
            Monitor ID
        """
        monitor_id = f"monitor_{int(time.time())}"
        
        self.monitors[monitor_id] = {
            "name": name,
            "topic": topic,
            "interval_hours": interval_hours,
            "sources": sources,
            "output_dir": output_dir or str(Path.home() / ".research-collector" / "results"),
            "created_at": datetime.now().isoformat(),
            "last_run": None,
            "enabled": True
        }
        
        self._save_monitors()
        return monitor_id
    
    def remove_monitor(self, monitor_id: str) -> bool:
        """Remove a monitor.
        
        Args:
            monitor_id: Monitor ID to remove
        
        Returns:
            True if removed, False if not found
        """
        if monitor_id in self.monitors:
            del self.monitors[monitor_id]
            self._save_monitors()
            return True
        return False
    
    def list_monitors(self) -> List[Dict]:
        """List all monitors."""
        return [
            {
                "id": mid,
                **monitor
            }
            for mid, monitor in self.monitors.items()
        ]
    
    def enable_monitor(self, monitor_id: str) -> bool:
        """Enable a monitor."""
        if monitor_id in self.monitors:
            self.monitors[monitor_id]["enabled"] = True
            self._save_monitors()
            return True
        return False
    
    def disable_monitor(self, monitor_id: str) -> bool:
        """Disable a monitor."""
        if monitor_id in self.monitors:
            self.monitors[monitor_id]["enabled"] = False
            self._save_monitors()
            return True
        return False
    
    def run_monitor(self, monitor_id: str) -> Optional[Dict]:
        """Run a single monitor check.
        
        Args:
            monitor_id: Monitor ID to run
        
        Returns:
            Research results or None if monitor not found
        """
        if monitor_id not in self.monitors:
            return None
        
        monitor = self.monitors[monitor_id]
        
        if not monitor.get("enabled", True):
            print(f"Monitor {monitor['name']} is disabled")
            return None
        
        print(f"Running monitor: {monitor['name']}")
        print(f"Topic: {monitor['topic']}")
        
        pipeline = Pipeline(self.config)
        
        from datetime import timedelta
        from_date = datetime.now() - timedelta(hours=monitor["interval_hours"])
        to_date = datetime.now()
        
        results = pipeline.run(
            topic=monitor["topic"],
            from_date=from_date,
            to_date=to_date,
            sources=monitor.get("sources")
        )
        
        # Save results
        output_path = Path(monitor["output_dir"]) / f"{monitor['name']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
        
        # Update last run time
        self.monitors[monitor_id]["last_run"] = datetime.now().isoformat()
        self._save_monitors()
        
        print(f"Found {len(results['items'])} new results")
        print(f"Results saved to {output_path}")
        
        return results
    
    def run_all_monitors(self) -> Dict[str, Any]:
        """Run all enabled monitors.
        
        Returns:
            Summary of results
        """
        results_summary = {}
        
        for monitor_id in self.monitors:
            if self.monitors[monitor_id].get("enabled", True):
                results = self.run_monitor(monitor_id)
                results_summary[monitor_id] = {
                    "name": self.monitors[monitor_id]["name"],
                    "count": len(results["items"]) if results else 0,
                    "success": results is not None
                }
        
        return results_summary
    
    def start_daemon(self, check_interval: int = 60) -> None:
        """Start monitor daemon (runs in foreground).
        
        Args:
            check_interval: Check interval in seconds
        """
        print(f"Starting monitor daemon (check interval: {check_interval}s)")
        print("Press Ctrl+C to stop")
        
        try:
            while True:
                now = datetime.now()
                
                for monitor_id, monitor in self.monitors.items():
                    if not monitor.get("enabled", True):
                        continue
                    
                    last_run = monitor.get("last_run")
                    if last_run:
                        last_run_time = datetime.fromisoformat(last_run)
                        hours_since_run = (now - last_run_time).total_seconds() / 3600
                        
                        if hours_since_run >= monitor["interval_hours"]:
                            print(f"\n[{now.strftime('%Y-%m-%d %H:%M:%S')}] Running monitor: {monitor['name']}")
                            self.run_monitor(monitor_id)
                    else:
                        # Never run, run now
                        print(f"\n[{now.strftime('%Y-%m-%d %H:%M:%S')}] Running monitor: {monitor['name']}")
                        self.run_monitor(monitor_id)
                
                time.sleep(check_interval)
                
        except KeyboardInterrupt:
            print("\nMonitor daemon stopped")
