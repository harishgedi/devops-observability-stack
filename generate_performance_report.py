#!/usr/bin/env python3
"""
Performance Metrics Generator for DevOps Observability Stack
Author: Gedi Harish | github.com/harishgedi
Generates comprehensive performance report and metrics
"""

import json
import time
import requests
import psutil
import sys
from datetime import datetime
from typing import Dict, List, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PerformanceReporter:
    """Generate comprehensive performance reports"""
    
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.metrics = {}
        
    def collect_system_performance(self) -> Dict[str, Any]:
        """Collect system performance metrics"""
        logger.info("Collecting system performance metrics...")
        
        # CPU performance
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        cpu_freq = psutil.cpu_freq()
        
        # Memory performance
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        # Disk performance
        disk = psutil.disk_usage('/')
        disk_io = psutil.disk_io_counters()
        
        # Network performance
        network = psutil.net_io_counters()
        
        # System info
        boot_time = psutil.boot_time()
        uptime = time.time() - boot_time
        
        return {
            "timestamp": datetime.now().isoformat(),
            "cpu": {
                "usage_percent": cpu_percent,
                "core_count": cpu_count,
                "frequency_mhz": cpu_freq.current if cpu_freq else 0,
                "load_average": list(psutil.getloadavg()) if hasattr(psutil, 'getloadavg') else [0, 0, 0]
            },
            "memory": {
                "total_gb": memory.total / (1024**3),
                "available_gb": memory.available / (1024**3),
                "used_gb": memory.used / (1024**3),
                "usage_percent": memory.percent,
                "swap_total_gb": swap.total / (1024**3),
                "swap_used_gb": swap.used / (1024**3),
                "swap_percent": swap.percent
            },
            "disk": {
                "total_gb": disk.total / (1024**3),
                "free_gb": disk.free / (1024**3),
                "used_gb": disk.used / (1024**3),
                "usage_percent": disk.percent,
                "read_bytes": disk_io.read_bytes if disk_io else 0,
                "write_bytes": disk_io.write_bytes if disk_io else 0
            },
            "network": {
                "bytes_sent": network.bytes_sent,
                "bytes_recv": network.bytes_recv,
                "packets_sent": network.packets_sent,
                "packets_recv": network.packets_recv
            },
            "system": {
                "uptime_hours": uptime / 3600,
                "process_count": len(psutil.pids()),
                "boot_time": datetime.fromtimestamp(boot_time).isoformat()
            }
        }
    
    def test_api_performance(self) -> Dict[str, Any]:
        """Test API endpoint performance"""
        logger.info("Testing API performance...")
        
        endpoints = [
            "/health",
            "/api/system-metrics",
            "/api/container-metrics", 
            "/metrics",
            "/alerts",
            "/dashboards"
        ]
        
        results = {}
        
        for endpoint in endpoints:
            try:
                # Test response time
                start_time = time.time()
                response = requests.get(f"{self.base_url}{endpoint}", timeout=10)
                response_time = time.time() - start_time
                
                # Get response size
                response_size = len(response.content) if response.content else 0
                
                results[endpoint] = {
                    "status_code": response.status_code,
                    "response_time_ms": round(response_time * 1000, 2),
                    "response_size_bytes": response_size,
                    "success": response.status_code == 200
                }
                
                logger.info(f"{endpoint}: {response_time*1000:.2f}ms")
                
            except Exception as e:
                results[endpoint] = {
                    "status_code": 0,
                    "response_time_ms": 0,
                    "response_size_bytes": 0,
                    "success": False,
                    "error": str(e)
                }
                logger.error(f"{endpoint}: FAILED - {e}")
        
        return results
    
    def collect_application_metrics(self) -> Dict[str, Any]:
        """Collect application-specific metrics"""
        logger.info("Collecting application metrics...")
        
        metrics = {}
        
        try:
            # Get system metrics from API
            response = requests.get(f"{self.base_url}/api/system-metrics", timeout=5)
            if response.status_code == 200:
                metrics["system_api"] = response.json()
            
            # Get container metrics
            response = requests.get(f"{self.base_url}/api/container-metrics", timeout=5)
            if response.status_code == 200:
                metrics["containers"] = response.json()
            
            # Get alert rules
            response = requests.get(f"{self.base_url}/alerts", timeout=5)
            if response.status_code == 200:
                alerts_data = response.json()
                metrics["alerts"] = {
                    "total_rules": len(alerts_data.get("rules", [])),
                    "rules": alerts_data.get("rules", [])
                }
            
            # Get dashboards
            response = requests.get(f"{self.base_url}/dashboards", timeout=5)
            if response.status_code == 200:
                dashboards_data = response.json()
                metrics["dashboards"] = {
                    "total_dashboards": len(dashboards_data.get("dashboards", [])),
                    "dashboards": dashboards_data.get("dashboards", [])
                }
            
        except Exception as e:
            logger.error(f"Failed to collect application metrics: {e}")
            metrics["error"] = str(e)
        
        return metrics
    
    def generate_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        logger.info("Generating performance report...")
        
        report = {
            "report_metadata": {
                "generated_at": datetime.now().isoformat(),
                "report_version": "1.0.0",
                "author": "Gedi Harish",
                "github": "github.com/harishgedi"
            },
            "system_performance": self.collect_system_performance(),
            "api_performance": self.test_api_performance(),
            "application_metrics": self.collect_application_metrics(),
            "performance_analysis": {}
        }
        
        # Add performance analysis
        api_results = report["api_performance"]
        successful_endpoints = [ep for ep, data in api_results.items() if data["success"]]
        
        report["performance_analysis"] = {
            "api_health": {
                "total_endpoints": len(api_results),
                "successful_endpoints": len(successful_endpoints),
                "success_rate": len(successful_endpoints) / len(api_results) * 100 if api_results else 0
            },
            "response_time_analysis": {
                "avg_response_time_ms": sum(data["response_time_ms"] for data in api_results.values()) / len(api_results) if api_results else 0,
                "max_response_time_ms": max(data["response_time_ms"] for data in api_results.values()) if api_results else 0,
                "min_response_time_ms": min(data["response_time_ms"] for data in api_results.values()) if api_results else 0
            },
            "system_health": {
                "cpu_usage": report["system_performance"]["cpu"]["usage_percent"],
                "memory_usage": report["system_performance"]["memory"]["usage_percent"],
                "disk_usage": report["system_performance"]["disk"]["usage_percent"],
                "uptime_hours": report["system_performance"]["system"]["uptime_hours"]
            }
        }
        
        return report
    
    def save_report(self, report: Dict[str, Any], filename: str = "performance_report.json"):
        """Save performance report to file"""
        with open(filename, "w") as f:
            json.dump(report, f, indent=2, default=str)
        logger.info(f"Performance report saved to {filename}")
    
    def print_summary(self, report: Dict[str, Any]):
        """Print performance summary"""
        print("\n" + "="*60)
        print("DEVOPS OBSERVABILITY STACK - PERFORMANCE REPORT")
        print("="*60)
        
        # API Performance Summary
        api_health = report["performance_analysis"]["api_health"]
        print(f"\nAPI Performance:")
        print(f"   Success Rate: {api_health['success_rate']:.1f}%")
        print(f"   Endpoints: {api_health['successful_endpoints']}/{api_health['total_endpoints']}")
        
        # Response Time Analysis
        rt_analysis = report["performance_analysis"]["response_time_analysis"]
        print(f"\nResponse Times:")
        print(f"   Average: {rt_analysis['avg_response_time_ms']:.2f}ms")
        print(f"   Min: {rt_analysis['min_response_time_ms']:.2f}ms")
        print(f"   Max: {rt_analysis['max_response_time_ms']:.2f}ms")
        
        # System Health
        sys_health = report["performance_analysis"]["system_health"]
        print(f"\nSystem Health:")
        print(f"   CPU Usage: {sys_health['cpu_usage']:.1f}%")
        print(f"   Memory Usage: {sys_health['memory_usage']:.1f}%")
        print(f"   Disk Usage: {sys_health['disk_usage']:.1f}%")
        print(f"   Uptime: {sys_health['uptime_hours']:.1f} hours")
        
        # Application Metrics
        app_metrics = report.get("application_metrics", {})
        if "alerts" in app_metrics:
            print(f"\nAlert Management:")
            print(f"   Alert Rules: {app_metrics['alerts']['total_rules']}")
        
        if "dashboards" in app_metrics:
            print(f"\nDashboards:")
            print(f"   Total Dashboards: {app_metrics['dashboards']['total_dashboards']}")
        
        if "containers" in app_metrics:
            containers = app_metrics["containers"]
            running = len([c for c in containers if c.get("status") == "running"])
            print(f"\nContainer Status:")
            print(f"   Running: {running}/{len(containers)} containers")
        
        print("\n" + "="*60)
        print("Performance report generated successfully!")
        print("Report saved to: performance_report.json")
        print("="*60)

def main():
    """Main execution"""
    reporter = PerformanceReporter()
    
    try:
        # Generate comprehensive report
        report = reporter.generate_performance_report()
        
        # Save report
        reporter.save_report(report)
        
        # Print summary
        reporter.print_summary(report)
        
        print(f"\nPerformance Metrics Summary:")
        print(f"   • API Success Rate: {report['performance_analysis']['api_health']['success_rate']:.1f}%")
        print(f"   • Avg Response Time: {report['performance_analysis']['response_time_analysis']['avg_response_time_ms']:.2f}ms")
        print(f"   • System CPU: {report['performance_analysis']['system_health']['cpu_usage']:.1f}%")
        print(f"   • System Memory: {report['performance_analysis']['system_health']['memory_usage']:.1f}%")
        print(f"   • Alert Rules: {report.get('application_metrics', {}).get('alerts', {}).get('total_rules', 0)}")
        print(f"   • Dashboards: {report.get('application_metrics', {}).get('dashboards', {}).get('total_dashboards', 0)}")
        
    except Exception as e:
        logger.error(f"Failed to generate performance report: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
