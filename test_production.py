#!/usr/bin/env python3
"""
Production Test Suite for DevOps Observability Stack
Author: Gedi Harish | github.com/harishgedi
Comprehensive testing for enterprise deployment readiness
"""

import asyncio
import json
import time
import sys
import os
import requests
import subprocess
import yaml
from pathlib import Path
from typing import Dict, List, Any
import logging
from dataclasses import dataclass

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class TestResult:
    """Test result data structure"""
    name: str
    status: str
    duration: float
    details: str
    timestamp: float

class ProductionTestSuite:
    """Comprehensive production test suite"""
    
    def __init__(self):
        self.results: List[TestResult] = []
        self.base_url = "http://localhost:8000"
        self.prometheus_url = "http://localhost:9090"
        self.grafana_url = "http://localhost:3000"
        self.alertmanager_url = "http://localhost:9093"
        
    def run_test(self, test_name: str, test_func) -> TestResult:
        """Run a single test and capture results"""
        start_time = time.time()
        try:
            result = test_func()
            duration = time.time() - start_time
            test_result = TestResult(
                name=test_name,
                status="PASS" if result else "FAIL",
                duration=duration,
                details="Test completed successfully" if result else "Test failed",
                timestamp=time.time()
            )
            logger.info(f"Test {test_name}: {test_result.status} ({duration:.2f}s)")
        except Exception as e:
            duration = time.time() - start_time
            test_result = TestResult(
                name=test_name,
                status="ERROR",
                duration=duration,
                details=str(e),
                timestamp=time.time()
            )
            logger.error(f"Test {test_name}: ERROR - {e}")
        
        self.results.append(test_result)
        return test_result
    
    def test_docker_installation(self) -> bool:
        """Test Docker installation and availability"""
        try:
            result = subprocess.run(['docker', '--version'], capture_output=True, text=True, timeout=10)
            return result.returncode == 0 and 'Docker' in result.stdout
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def test_docker_compose_installation(self) -> bool:
        """Test Docker Compose installation"""
        try:
            # Try docker-compose first
            result = subprocess.run(['docker-compose', '--version'], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                return True
            
            # Try docker compose (newer syntax)
            result = subprocess.run(['docker', 'compose', 'version'], capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def test_configuration_files(self) -> bool:
        """Test configuration file validity"""
        config_files = [
            'config/prometheus.yml',
            'config/alertmanager.yml',
            'config/alert_rules.yml',
            'docker-compose.yml'
        ]
        
        for config_file in config_files:
            if not os.path.exists(config_file):
                logger.error(f"Missing config file: {config_file}")
                return False
            
            try:
                with open(config_file, 'r') as f:
                    if config_file.endswith('.yml') or config_file.endswith('.yaml'):
                        yaml.safe_load(f)
            except yaml.YAMLError as e:
                logger.error(f"Invalid YAML in {config_file}: {e}")
                return False
        
        return True
    
    def test_monitoring_service_health(self) -> bool:
        """Test monitoring service health endpoint"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                return data.get('status') == 'healthy'
            return False
        except requests.RequestException:
            return False
    
    def test_system_metrics_endpoint(self) -> bool:
        """Test system metrics collection"""
        try:
            response = requests.get(f"{self.base_url}/api/system-metrics", timeout=5)
            if response.status_code == 200:
                data = response.json()
                required_fields = ['cpu_percent', 'memory_percent', 'disk_usage_percent', 'timestamp']
                return all(field in data for field in required_fields)
            return False
        except requests.RequestException:
            return False
    
    def test_container_metrics_endpoint(self) -> bool:
        """Test container metrics collection"""
        try:
            response = requests.get(f"{self.base_url}/api/container-metrics", timeout=5)
            return response.status_code == 200 and isinstance(response.json(), list)
        except requests.RequestException:
            return False
    
    def test_prometheus_metrics_endpoint(self) -> bool:
        """Test Prometheus metrics format"""
        try:
            response = requests.get(f"{self.base_url}/metrics", timeout=5)
            if response.status_code == 200:
                metrics_text = response.text
                # Check for expected metric names
                expected_metrics = [
                    'system_cpu_percent',
                    'system_memory_percent',
                    'api_requests_total'
                ]
                return any(metric in metrics_text for metric in expected_metrics)
            return False
        except requests.RequestException:
            return False
    
    def test_alert_management(self) -> bool:
        """Test alert rule management"""
        try:
            # Test getting alerts
            response = requests.get(f"{self.base_url}/alerts", timeout=5)
            if response.status_code != 200:
                return False
            
            alerts_data = response.json()
            if 'rules' not in alerts_data:
                return False
            
            # Test creating alert
            alert_data = {
                "name": "TestAlert",
                "expr": "system_cpu_percent > 90",
                "severity": "warning",
                "message": "Test alert for high CPU"
            }
            
            response = requests.post(f"{self.base_url}/alerts", json=alert_data, timeout=5)
            if response.status_code != 200:
                return False
            
            # Clean up - delete test alert
            response = requests.delete(f"{self.base_url}/alerts/TestAlert", timeout=5)
            return response.status_code == 200
            
        except requests.RequestException:
            return False
    
    def test_dashboard_generation(self) -> bool:
        """Test Grafana dashboard generation"""
        try:
            response = requests.get(f"{self.base_url}/dashboards", timeout=5)
            if response.status_code == 200:
                dashboards_data = response.json()
                return 'dashboards' in dashboards_data and len(dashboards_data['dashboards']) > 0
            return False
        except requests.RequestException:
            return False
    
    def test_prometheus_connectivity(self) -> bool:
        """Test Prometheus server connectivity"""
        try:
            response = requests.get(f"{self.prometheus_url}/-/healthy", timeout=5)
            return response.status_code == 200
        except requests.RequestException:
            return False
    
    def test_grafana_connectivity(self) -> bool:
        """Test Grafana server connectivity"""
        try:
            response = requests.get(f"{self.grafana_url}/api/health", timeout=5)
            return response.status_code == 200
        except requests.RequestException:
            return False
    
    def test_alertmanager_connectivity(self) -> bool:
        """Test AlertManager server connectivity"""
        try:
            response = requests.get(f"{self.alertmanager_url}/-/healthy", timeout=5)
            return response.status_code == 200
        except requests.RequestException:
            return False
    
    def test_performance_benchmarks(self) -> bool:
        """Test performance benchmarks"""
        try:
            # Test API response time
            start_time = time.time()
            response = requests.get(f"{self.base_url}/api/system-metrics", timeout=5)
            response_time = time.time() - start_time
            
            # API should respond in under 2 seconds
            if response_time > 2.0:
                logger.warning(f"Slow API response: {response_time:.2f}s")
                return False
            
            # Test metrics collection performance
            start_time = time.time()
            response = requests.get(f"{self.base_url}/metrics", timeout=5)
            metrics_time = time.time() - start_time
            
            # Metrics should be generated in under 1 second
            if metrics_time > 1.0:
                logger.warning(f"Slow metrics generation: {metrics_time:.2f}s")
                return False
            
            return True
            
        except requests.RequestException:
            return False
    
    def test_error_handling(self) -> bool:
        """Test error handling and resilience"""
        try:
            # Test 404 handling
            response = requests.get(f"{self.base_url}/nonexistent", timeout=5)
            if response.status_code != 404:
                return False
            
            # Test invalid alert creation
            invalid_alert = {"name": "", "expr": "invalid"}
            response = requests.post(f"{self.base_url}/alerts", json=invalid_alert, timeout=5)
            if response.status_code not in [400, 422]:
                return False
            
            return True
            
        except requests.RequestException:
            return False
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all production tests"""
        logger.info("Starting Production Test Suite")
        logger.info("=" * 50)
        
        # Infrastructure tests
        self.run_test("Docker Installation", self.test_docker_installation)
        self.run_test("Docker Compose Installation", self.test_docker_compose_installation)
        self.run_test("Configuration Files", self.test_configuration_files)
        
        # Service health tests
        self.run_test("Monitoring Service Health", self.test_monitoring_service_health)
        self.run_test("Prometheus Connectivity", self.test_prometheus_connectivity)
        self.run_test("Grafana Connectivity", self.test_grafana_connectivity)
        self.run_test("AlertManager Connectivity", self.test_alertmanager_connectivity)
        
        # API functionality tests
        self.run_test("System Metrics Endpoint", self.test_system_metrics_endpoint)
        self.run_test("Container Metrics Endpoint", self.test_container_metrics_endpoint)
        self.run_test("Prometheus Metrics Endpoint", self.test_prometheus_metrics_endpoint)
        self.run_test("Alert Management", self.test_alert_management)
        self.run_test("Dashboard Generation", self.test_dashboard_generation)
        
        # Performance and reliability tests
        self.run_test("Performance Benchmarks", self.test_performance_benchmarks)
        self.run_test("Error Handling", self.test_error_handling)
        
        # Generate summary
        total_tests = len(self.results)
        passed_tests = len([r for r in self.results if r.status == "PASS"])
        failed_tests = len([r for r in self.results if r.status == "FAIL"])
        error_tests = len([r for r in self.results if r.status == "ERROR"])
        
        summary = {
            "test_summary": {
                "total_tests": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "errors": error_tests,
                "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0
            },
            "test_results": [
                {
                    "name": r.name,
                    "status": r.status,
                    "duration": r.duration,
                    "details": r.details,
                    "timestamp": r.timestamp
                }
                for r in self.results
            ],
            "timestamp": time.time()
        }
        
        # Print results
        logger.info("=" * 50)
        logger.info(f"Test Results: {passed_tests}/{total_tests} passed ({summary['test_summary']['success_rate']:.1f}%)")
        
        if failed_tests > 0 or error_tests > 0:
            logger.warning("Failed tests:")
            for result in self.results:
                if result.status in ["FAIL", "ERROR"]:
                    logger.warning(f"  - {result.name}: {result.details}")
        
        return summary

def main():
    """Main test execution"""
    test_suite = ProductionTestSuite()
    results = test_suite.run_all_tests()
    
    # Save results to file
    with open("production_test_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    logger.info("Production test results saved to production_test_results.json")
    
    # Exit with appropriate code
    failed_count = results["test_summary"]["failed"] + results["test_summary"]["errors"]
    sys.exit(0 if failed_count == 0 else 1)

if __name__ == "__main__":
    main()
