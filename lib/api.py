"""
slckr API Client - Authentication and communication with api.slckr.xyz backend
Handles error reporting, telemetry, and client secret management
"""

import requests
import json
import uuid
import os
import platform
import sys
from pathlib import Path
from typing import Dict, Optional, Tuple


class SlckrAPIClient:
    """Client for communicating with slckr.xyz backend API"""

    BASE_URL = "https://api.slckr.xyz"
    SECRET_FILE = Path.home() / ".hwhelper" / "client_secret.json"

    def __init__(self):
        self.client_id = None
        self.client_secret = None
        self._load_or_create_secret()

    def _load_or_create_secret(self):
        """Load existing client secret or generate new one"""
        secret_path = self.SECRET_FILE
        secret_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            if secret_path.exists():
                # Load existing secret
                with open(secret_path, 'r') as f:
                    data = json.load(f)
                    self.client_id = data.get('client_id')
                    self.client_secret = data.get('client_secret')

                if self.client_id and self.client_secret:
                    print(f"✓ Loaded client credentials (ID: {self.client_id[:8]}...)")
                    return

            # Generate new secret
            self.client_id = str(uuid.uuid4())
            self.client_secret = str(uuid.uuid4())

            # Save to file
            with open(secret_path, 'w') as f:
                json.dump({
                    'client_id': self.client_id,
                    'client_secret': self.client_secret
                }, f, indent=2)

            print(f"✓ Generated new client credentials (ID: {self.client_id[:8]}...)")

        except Exception as e:
            print(f"⚠️ Could not load/create client secret: {e}")
            # Fallback to temporary in-memory secret
            self.client_id = str(uuid.uuid4())
            self.client_secret = str(uuid.uuid4())

    def _get_headers(self) -> Dict[str, str]:
        """Get API headers with authentication"""
        return {
            'X-Client-Secret': self.client_secret
        }

    def _make_request(self, method: str, endpoint: str, **kwargs) -> Optional[Dict]:
        """Make authenticated request to API"""
        url = f"{self.BASE_URL}{endpoint}"
        headers = kwargs.pop('headers', {})
        headers.update(self._get_headers())

        try:
            response = requests.request(
                method,
                url,
                headers=headers,
                timeout=kwargs.pop('timeout', 15),
                **kwargs
            )
            response.raise_for_status()
            return response.json()

        except requests.exceptions.Timeout:
            print(f"⚠️ API request timed out: {endpoint}")
            return None
        except requests.exceptions.ConnectionError:
            print(f"⚠️ Could not connect to API: {endpoint}")
            return None
        except requests.exceptions.HTTPError as e:
            print(f"⚠️ API error ({e.response.status_code}): {e.response.text[:200]}")
            return None
        except Exception as e:
            print(f"⚠️ Unexpected API error: {e}")
            return None

    def health_check(self) -> bool:
        """Check if API is reachable"""
        try:
            response = requests.get(f"{self.BASE_URL}/api/health", timeout=5)
            return response.status_code == 200
        except:
            return False

    def send_telemetry(self, version: str, os_name: str, python_version: str) -> bool:
        """Send telemetry ping on app startup"""
        try:
            data = {
                'client_id': self.client_id,
                'version': version,
                'os': os_name,
                'python_version': python_version
            }

            result = self._make_request('POST', '/api/telemetry', json=data)

            if result and result.get('status') == 'success':
                print(f"✓ Telemetry sent (v{version})")
                return True
            else:
                print("⚠️ Telemetry failed")
                return False

        except Exception as e:
            print(f"⚠️ Telemetry error: {e}")
            return False

    def send_report(
        self,
        error_message: str,
        version: str,
        os_name: str,
        python_version: str,
        widget_tree_json: Optional[Dict] = None,
        ai_response_json: Optional[Dict] = None,
        system_info_json: Optional[Dict] = None,
        question_screenshot_path: Optional[str] = None,
        answer_screenshot_path: Optional[str] = None
    ) -> Optional[str]:
        """
        Send error report to backend

        Returns:
            Report ID if successful, None otherwise
        """
        try:
            # Prepare report data (matching backend field names)
            report_data = {
                'client_id': self.client_id,
                'version': version,
                'os': os_name,
                'python_version': python_version,
                'error_message': error_message
            }

            # Add JSON fields if provided (matching backend field names)
            if widget_tree_json:
                report_data['widget_tree_json'] = widget_tree_json
            if ai_response_json:
                report_data['ai_response_data'] = ai_response_json  # Backend expects 'ai_response_data'
            if system_info_json:
                report_data['system_info'] = system_info_json  # Backend expects 'system_info'

            # Prepare file uploads
            files = {}
            file_handles = []

            try:
                if question_screenshot_path and os.path.exists(question_screenshot_path):
                    fh = open(question_screenshot_path, 'rb')
                    files['question_screenshot'] = ('question.png', fh, 'image/png')
                    file_handles.append(fh)

                if answer_screenshot_path and os.path.exists(answer_screenshot_path):
                    fh = open(answer_screenshot_path, 'rb')
                    files['answer_screenshot'] = ('answer.png', fh, 'image/png')
                    file_handles.append(fh)

                # Send request with proper format
                if files:
                    # Multipart request: Send JSON as 'report_data' form field
                    form_data = {
                        'report_data': json.dumps(report_data, default=str)
                    }
                    result = self._make_request(
                        'POST',
                        '/api/report',
                        data=form_data,
                        files=files
                    )
                else:
                    # Pure JSON request (no files)
                    result = self._make_request(
                        'POST',
                        '/api/report',
                        json=report_data
                    )

            finally:
                # Always close file handles
                for fh in file_handles:
                    try:
                        fh.close()
                    except:
                        pass

            if result and result.get('status') == 'success':
                report_id = result.get('report_id')
                print(f"✓ Error report sent (ID: {report_id})")

                # Clean up temp answer screenshot
                if answer_screenshot_path and os.path.exists(answer_screenshot_path):
                    try:
                        os.remove(answer_screenshot_path)
                    except:
                        pass

                return report_id
            else:
                print(f"⚠️ Error report failed: {result.get('message', 'Unknown error') if result else 'No response'}")
                return None

        except Exception as e:
            print(f"⚠️ Could not send error report: {e}")
            return None

    def get_stats(self, admin_token: str) -> Optional[Dict]:
        """
        Get installation statistics (admin only)

        Args:
            admin_token: Admin API token

        Returns:
            Stats dict if successful, None otherwise
        """
        try:
            headers = {'X-Admin-Token': admin_token}
            result = self._make_request('GET', '/api/stats', headers=headers)
            return result
        except Exception as e:
            print(f"⚠️ Could not fetch stats: {e}")
            return None


# Test function for development
if __name__ == "__main__":
    print("=== slckr API Client Test ===\n")

    client = SlckrAPIClient()

    print("\n1. Testing health check...")
    if client.health_check():
        print("✓ API is reachable")
    else:
        print("✗ API is unreachable")

    print("\n2. Testing telemetry...")
    client.send_telemetry("1.0.50")

    print("\n3. Testing error report...")
    report_id = client.send_report(
        error_message="Test error from api_client.py",
        system_info_json={
            "os": platform.system(),
            "python": sys.version
        }
    )
    if report_id:
        print(f"✓ Test report submitted: {report_id}")

    print("\n=== Test Complete ===")
