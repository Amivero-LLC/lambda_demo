import json
import os
from collections import defaultdict
from datetime import datetime, timezone
from typing import Dict, List, Any

class LogAnalyzer:
    def __init__(self, logs: List[Dict[str, Any]]):
        self.logs = logs
        self.total_requests = len(logs)
        self.status_codes = defaultdict(int)
        self.endpoints = defaultdict(int)
        self.errors = 0
        self.response_times = []
        self.error_messages = defaultdict(int)
        
    def analyze(self) -> Dict[str, Any]:
        for log in self.logs:
            # Count status codes
            status = log.get('status', 200)
            self.status_codes[status] += 1
            
            # Count errors (4xx and 5xx)
            if 400 <= status < 600:
                self.errors += 1
                error_msg = log.get('message', 'No error message')
                self.error_messages[error_msg] += 1
            
            # Track endpoints
            endpoint = log.get('path', 'unknown')
            self.endpoints[endpoint] += 1
            
            # Track response times if available
            if 'response_time' in log:
                self.response_times.append(log['response_time'])
        
        # Calculate metrics
        error_rate = (self.errors / self.total_requests) * 100 if self.total_requests > 0 else 0
        avg_response_time = sum(self.response_times) / len(self.response_times) if self.response_times else 0
        
        return {
            'total_requests': self.total_requests,
            'error_rate_percentage': round(error_rate, 2),
            'status_code_distribution': dict(self.status_codes),
            'top_endpoints': dict(sorted(self.endpoints.items(), key=lambda x: x[1], reverse=True)[:5]),
            'avg_response_time_ms': round(avg_response_time, 2) if self.response_times else 'N/A',
            'top_errors': dict(sorted(self.error_messages.items(), key=lambda x: x[1], reverse=True)[:3])
        }

def lambda_handler(event, context):
    print("Event: ", json.dumps(event, indent=2))
    
    # Sample log data - in production, this would come from CloudWatch or another source
    sample_logs = [
        {'timestamp': '2023-08-14T10:00:00', 'path': '/api/users', 'status': 200, 'method': 'GET', 'response_time': 45},
        {'timestamp': '2023-08-14T10:00:01', 'path': '/api/orders', 'status': 201, 'method': 'POST', 'response_time': 120},
        {'timestamp': '2023-08-14T10:00:02', 'path': '/api/products', 'status': 404, 'method': 'GET', 'response_time': 15, 'message': 'Product not found'},
        {'timestamp': '2023-08-14T10:00:03', 'path': '/api/users', 'status': 200, 'method': 'GET', 'response_time': 50},
        {'timestamp': '2023-08-14T10:00:04', 'path': '/api/orders', 'status': 500, 'method': 'POST', 'response_time': 200, 'message': 'Internal server error'},
    ]
    
    # In a real scenario, you would extract logs from the event
    # For example, if logs come in the request body:
    # request_logs = json.loads(event.get('body', '[]'))
    
    analyzer = LogAnalyzer(sample_logs)
    analysis = analyzer.analyze()
    
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps({
            "analysis": analysis,
            "environment": os.environ.get('ENVIRONMENT', 'development'),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }, indent=2)
    }
    