#!/usr/bin/env python3
"""
Error Reporting API Server
===========================
Lightweight Flask API for collecting error reports from Homework Helper clients.
Stores reports in SQLite database and provides basic admin interface.

Setup:
    pip install flask flask-cors
    python error_server.py

Production Deployment:
    Use gunicorn or waitress for production serving:
    pip install gunicorn
    gunicorn -w 4 -b 0.0.0.0:5000 error_server:app
"""

from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import sqlite3
import json
import os
from datetime import datetime
from pathlib import Path

app = Flask(__name__)
CORS(app)  # Enable CORS for cross-origin requests

# Database configuration
DB_PATH = Path(__file__).parent / 'error_reports.db'
UPLOAD_FOLDER = Path(__file__).parent / 'uploads'
UPLOAD_FOLDER.mkdir(exist_ok=True)

# Maximum upload size (10MB)
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024


def init_database():
    """Initialize SQLite database with schema"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS error_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            version TEXT,
            os_info TEXT,
            python_version TEXT,
            error_message TEXT,
            full_report TEXT,
            screenshot_path TEXT,
            answer_display_path TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()


@app.route('/api/report', methods=['POST'])
def receive_report():
    """
    Receive error report from client

    Expects JSON payload with error details and optional file uploads
    """
    try:
        # Parse JSON data
        if request.is_json:
            report_data = request.json
        else:
            # Try to get from form data
            report_json = request.form.get('report_data')
            if report_json:
                report_data = json.loads(report_json)
            else:
                return jsonify({'status': 'error', 'message': 'No JSON data provided'}), 400

        # Extract key fields
        timestamp = report_data.get('timestamp', datetime.utcnow().isoformat())
        version = report_data.get('version', 'Unknown')
        system_info = report_data.get('system', {})
        os_info = system_info.get('os', 'Unknown')
        python_version = system_info.get('python_version', 'Unknown')
        error_message = report_data.get('last_error', 'No error message')

        # Handle file uploads
        screenshot_path = None
        answer_display_path = None

        if 'screenshot' in request.files:
            screenshot = request.files['screenshot']
            if screenshot.filename:
                screenshot_path = UPLOAD_FOLDER / f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{screenshot.filename}"
                screenshot.save(screenshot_path)

        if 'answer_display' in request.files:
            answer_display = request.files['answer_display']
            if answer_display.filename:
                answer_display_path = UPLOAD_FOLDER / f"answer_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{answer_display.filename}"
                answer_display.save(answer_display_path)

        # Store in database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO error_reports (
                timestamp, version, os_info, python_version,
                error_message, full_report, screenshot_path, answer_display_path
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            timestamp, version, os_info, python_version,
            error_message, json.dumps(report_data),
            str(screenshot_path) if screenshot_path else None,
            str(answer_display_path) if answer_display_path else None
        ))

        conn.commit()
        report_id = cursor.lastrowid
        conn.close()

        print(f"✓ Received error report #{report_id} from v{version} ({os_info})")

        return jsonify({
            'status': 'success',
            'message': 'Error report received',
            'report_id': report_id
        }), 200

    except Exception as e:
        print(f"✗ Error processing report: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/reports', methods=['GET'])
def list_reports():
    """
    List all error reports (admin endpoint)

    Query parameters:
        - limit: Number of reports to return (default 50)
        - offset: Pagination offset (default 0)
    """
    try:
        limit = int(request.args.get('limit', 50))
        offset = int(request.args.get('offset', 0))

        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id, timestamp, version, os_info, python_version,
                   error_message, created_at, screenshot_path, answer_display_path
            FROM error_reports
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
        ''', (limit, offset))

        reports = []
        for row in cursor.fetchall():
            reports.append({
                'id': row['id'],
                'timestamp': row['timestamp'],
                'version': row['version'],
                'os_info': row['os_info'],
                'python_version': row['python_version'],
                'error_message': row['error_message'][:200] if row['error_message'] else None,
                'created_at': row['created_at'],
                'has_screenshot': row['screenshot_path'] is not None,
                'has_answer_display': row['answer_display_path'] is not None
            })

        # Get total count
        cursor.execute('SELECT COUNT(*) FROM error_reports')
        total_count = cursor.fetchone()[0]

        conn.close()

        return jsonify({
            'status': 'success',
            'reports': reports,
            'total': total_count,
            'limit': limit,
            'offset': offset
        }), 200

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/reports/<int:report_id>', methods=['GET'])
def get_report_detail(report_id):
    """Get full details for a specific error report"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM error_reports WHERE id = ?
        ''', (report_id,))

        row = cursor.fetchone()
        conn.close()

        if not row:
            return jsonify({
                'status': 'error',
                'message': 'Report not found'
            }), 404

        report = {
            'id': row['id'],
            'timestamp': row['timestamp'],
            'version': row['version'],
            'os_info': row['os_info'],
            'python_version': row['python_version'],
            'error_message': row['error_message'],
            'full_report': json.loads(row['full_report']) if row['full_report'] else None,
            'created_at': row['created_at'],
            'screenshot_path': row['screenshot_path'],
            'answer_display_path': row['answer_display_path']
        }

        return jsonify({
            'status': 'success',
            'report': report
        }), 200

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/')
def admin_dashboard():
    """Simple admin dashboard for viewing reports"""
    html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Error Reports Dashboard</title>
        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Arial, sans-serif; margin: 20px; background: #f5f5f5; }
            h1 { color: #333; }
            .stats { background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            .report-list { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            .report-item { border-bottom: 1px solid #eee; padding: 15px 0; }
            .report-item:last-child { border-bottom: none; }
            .report-header { font-weight: bold; color: #d63031; }
            .report-meta { color: #636e72; font-size: 14px; margin-top: 5px; }
            .error-preview { background: #f8f9fa; padding: 10px; border-radius: 4px; margin-top: 10px; font-family: monospace; font-size: 12px; }
        </style>
    </head>
    <body>
        <h1>🚨 Error Reports Dashboard</h1>
        <div class="stats" id="stats">Loading statistics...</div>
        <div class="report-list" id="reports">Loading reports...</div>

        <script>
            // Fetch and display reports
            fetch('/api/reports?limit=20')
                .then(res => res.json())
                .then(data => {
                    // Update stats
                    document.getElementById('stats').innerHTML = `
                        <strong>Total Reports:</strong> ${data.total}
                    `;

                    // Display reports
                    const reportsDiv = document.getElementById('reports');
                    if (data.reports.length === 0) {
                        reportsDiv.innerHTML = '<p>No error reports yet.</p>';
                        return;
                    }

                    let html = '<h2>Recent Reports</h2>';
                    data.reports.forEach(report => {
                        html += `
                            <div class="report-item">
                                <div class="report-header">Report #${report.id} - v${report.version}</div>
                                <div class="report-meta">
                                    ${report.os_info} | ${report.python_version}<br>
                                    ${report.created_at}
                                </div>
                                <div class="error-preview">${report.error_message || 'No error message'}</div>
                            </div>
                        `;
                    });
                    reportsDiv.innerHTML = html;
                })
                .catch(err => {
                    document.getElementById('reports').innerHTML = '<p>Error loading reports: ' + err + '</p>';
                });
        </script>
    </body>
    </html>
    '''
    return render_template_string(html)


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'error-reporting-api',
        'timestamp': datetime.utcnow().isoformat()
    }), 200


if __name__ == '__main__':
    # Initialize database on startup
    init_database()
    print("=" * 60)
    print("Error Reporting API Server")
    print("=" * 60)
    print(f"Database: {DB_PATH}")
    print(f"Uploads: {UPLOAD_FOLDER}")
    print("\nEndpoints:")
    print("  POST /api/report          - Receive error reports")
    print("  GET  /api/reports         - List all reports")
    print("  GET  /api/reports/<id>    - Get report details")
    print("  GET  /                    - Admin dashboard")
    print("  GET  /health              - Health check")
    print("\nStarting server on http://0.0.0.0:5000")
    print("=" * 60)

    # Development server (use gunicorn for production)
    app.run(host='0.0.0.0', port=5000, debug=False)
