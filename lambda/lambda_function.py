import json
import os
from collections import defaultdict
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import statistics
import math

@dataclass
class LogEntry:
    timestamp: str
    path: str
    status: int
    method: str
    response_time: Optional[float] = None
    message: Optional[str] = None

class LogAnalyzer:
    def __init__(self, logs: List[Dict[str, Any]], page_size: int = 1000):
        self.logs = self._validate_and_parse_logs(logs)
        self.page_size = page_size
        self.total_requests = len(logs)
        self.status_codes = defaultdict(int)
        self.endpoints = defaultdict(lambda: {'count': 0, 'methods': defaultdict(int)})
        self.errors = 0
        self.response_times = []
        self.error_messages = defaultdict(int)
        self.methods = defaultdict(int)
        
    def _validate_and_parse_logs(self, logs: List[Dict[str, Any]]) -> List[LogEntry]:
        """Validate log entries and parse them into LogEntry objects."""
        if not isinstance(logs, list):
            raise ValueError("Input must be a list of log entries")
            
        parsed_logs = []
        for i, log in enumerate(logs, 1):
            try:
                # Required fields
                entry = LogEntry(
                    timestamp=log.get('timestamp', ''),
                    path=log.get('path', 'unknown'),
                    status=int(log.get('status', 200)),
                    method=str(log.get('method', 'UNKNOWN')).upper(),
                    response_time=float(log['response_time']) if 'response_time' in log else None,
                    message=log.get('message')
                )
                parsed_logs.append(entry)
            except (ValueError, TypeError) as e:
                print(f"Warning: Invalid log entry at position {i}: {e}")
                continue
                
        return parsed_logs

    def _process_log_page(self, page: List[LogEntry]) -> None:
        """Process a single page of logs."""
        for log in page:
            # Count status codes
            self.status_codes[log.status] += 1
            
            # Track methods
            self.methods[log.method] += 1
            
            # Count errors (4xx and 5xx)
            if 400 <= log.status < 600:
                self.errors += 1
                error_msg = log.message or 'No error message'
                self.error_messages[error_msg] += 1
            
            # Track endpoints and methods
            self.endpoints[log.path]['count'] += 1
            self.endpoints[log.path]['methods'][log.method] += 1
            
            # Track response times if available
            if log.response_time is not None:
                self.response_times.append(log.response_time)

    def _paginate_logs(self) -> List[List[LogEntry]]:
        """Split logs into pages for processing."""
        return [self.logs[i:i + self.page_size] 
                for i in range(0, len(self.logs), self.page_size)]

    def _calculate_percentile(self, percentile: float) -> float:
        """Calculate percentile from response times using statistics module."""
        if not self.response_times:
            return 0.0
    
        # Sort the response times
        sorted_times = sorted(self.response_times)
        n = len(sorted_times)
    
        # Calculate the index
        k = (n - 1) * (percentile / 100)
        f = math.floor(k)
        c = math.ceil(k)
    
        if f == c:
            return float(sorted_times[int(k)])
    
        # Linear interpolation
        d0 = sorted_times[int(f)] * (c - k)
        d1 = sorted_times[int(c)] * (k - f)
        return float(d0 + d1)

    def analyze(self) -> Dict[str, Any]:
        """Analyze logs with pagination support."""
        # Process logs in pages
        for page in self._paginate_logs():
            self._process_log_page(page)
        
        # Calculate metrics
        error_rate = (self.errors / self.total_requests * 100) if self.total_requests > 0 else 0
        avg_response_time = statistics.mean(self.response_times) if self.response_times else 0
        
        # Get top endpoints with method information
        top_endpoints = {
            path: {
                'total_requests': data['count'],
                'methods': dict(data['methods'])
            }
            for path, data in sorted(
                self.endpoints.items(),
                key=lambda x: x[1]['count'],
                reverse=True
            )[:5]
        }

        return {
            'total_requests': self.total_requests,
            'error_rate_percentage': round(error_rate, 2),
            'status_code_distribution': dict(self.status_codes),
            'method_distribution': dict(self.methods),
            'top_endpoints': top_endpoints,
            'response_times': {
                'avg_ms': round(avg_response_time, 2) if self.response_times else 0,
                'p50_ms': round(self._calculate_percentile(50), 2),
                'p95_ms': round(self._calculate_percentile(95), 2),
                'p99_ms': round(self._calculate_percentile(99), 2),
                'min_ms': round(min(self.response_times), 2) if self.response_times else 0,
                'max_ms': round(max(self.response_times), 2) if self.response_times else 0,
            },
            'top_errors': dict(sorted(
                self.error_messages.items(),
                key=lambda x: x[1],
                reverse=True
            )[:3])
        }

def lambda_handler(event, context):
    print("Event: ", json.dumps(event, indent=2))
    
    try:
        # Get logs from event or use sample data
        logs = event.get('logs', [
            {'timestamp': '2023-08-14T10:00:00', 'path': '/api/users', 'status': 200, 
             'method': 'GET', 'response_time': 45},
            {'timestamp': '2023-08-14T10:00:01', 'path': '/api/orders', 'status': 201, 
             'method': 'POST', 'response_time': 120},
            {'timestamp': '2023-08-14T10:00:02', 'path': '/api/products', 'status': 404, 
             'method': 'GET', 'response_time': 15, 'message': 'Product not found'},
            {'timestamp': '2023-08-14T10:00:03', 'path': '/api/users', 'status': 200, 
             'method': 'GET', 'response_time': 50},
            {'timestamp': '2023-08-14T10:00:04', 'path': '/api/orders', 'status': 500, 
             'method': 'POST', 'response_time': 200, 'message': 'Internal server error'},
        ])
        
        analyzer = LogAnalyzer(logs)
        analysis = analyzer.analyze()
        
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "analysis": analysis,
                "environment": os.environ.get('ENVIRONMENT', 'development'),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }, indent=2)
        }
        
    except Exception as e:
        return {
            "statusCode": 400,
            "body": json.dumps({
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
        }