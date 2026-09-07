import os
import json
import matplotlib
matplotlib.use('Agg') # Headless backend
import matplotlib.pyplot as plt
from datetime import datetime
from typing import List
from src.testing.types import TestRunResult
from src.testing.consistency_analyzer import ConsistencyAnalyzer

def format_timestamp(ts: str) -> str:
    try:
        dt = datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ")
        return dt.strftime("%d/%m/%Y %H:%M:%S")
    except Exception:
        return ts

class DashboardGenerator:
    @staticmethod
    def generate_dashboard(result: TestRunResult, base_dir: str = "results/dashboards") -> str:
        os.makedirs(base_dir, exist_ok=True)
        graphs_dir = os.path.join(base_dir, "graphs")
        os.makedirs(graphs_dir, exist_ok=True)
        
        timestamps = []
        values = []
        for i, m in enumerate(result.measurements):
            if m.success and m.value is not None:
                timestamps.append(i) # using index as simplified time axis
                values.append(m.value)
                
        time_series_path = os.path.join(graphs_dir, f"time_{result.test_id}.png")
        plt.figure(figsize=(8, 4))
        plt.plot(timestamps, values, marker='o', linestyle='-', color='#007acc', linewidth=2)
        plt.title(f"{result.ammeter_type.upper()} - Current over Time", fontsize=14)
        plt.xlabel("Sample Index", fontsize=12)
        plt.ylabel("Current (A)", fontsize=12)
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.tight_layout()
        plt.savefig(time_series_path)
        plt.close()
        
        hist_path = os.path.join(graphs_dir, f"hist_{result.test_id}.png")
        plt.figure(figsize=(8, 4))
        plt.hist(values, bins=10, color='#28a745', edgecolor='black', alpha=0.7)
        plt.title(f"{result.ammeter_type.upper()} - Value Distribution", fontsize=14)
        plt.xlabel("Current (A)", fontsize=12)
        plt.ylabel("Frequency", fontsize=12)
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.tight_layout()
        plt.savefig(hist_path)
        plt.close()
        
        html_path = os.path.join(base_dir, f"run_{result.test_id}.html")
        stats = result.statistics
        formatted_time = format_timestamp(result.timestamp)
        
        errors_html = ""
        if result.errors:
            errors_html = "<div class='errors'><h2>Errors</h2><ul>"
            for e in result.errors[:10]:
                err_time = format_timestamp(e.get('timestamp', ''))
                errors_html += f"<li>[{err_time}] <strong>{e.get('error_type')}</strong>: {e.get('error_message')}</li>"
            if len(result.errors) > 10:
                errors_html += f"<li>... and {len(result.errors) - 10} more.</li>"
            errors_html += "</ul></div>"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Test Report - {result.test_id}</title>
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f8f9fa; color: #212529; margin: 0; padding: 40px; }}
                h1, h2, h3 {{ color: #343a40; margin-bottom: 15px; }}
                .container {{ max-width: 1100px; margin: 0 auto; background: #ffffff; padding: 40px; border-radius: 12px; box-shadow: 0 10px 30px rgba(0,0,0,0.05); }}
                .header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; padding-bottom: 20px; border-bottom: 1px solid #dee2e6; }}
                .status {{ font-size: 20px; font-weight: bold; padding: 8px 16px; border-radius: 6px; letter-spacing: 1px; }}
                .status.pass {{ background-color: #d1e7dd; color: #0f5132; }}
                .status.fail {{ background-color: #f8d7da; color: #842029; }}
                .status.error {{ background-color: #fff3cd; color: #664d03; }}
                .meta-info p {{ margin: 5px 0; color: #6c757d; font-size: 15px; }}
                table {{ width: 100%; border-collapse: collapse; margin-bottom: 30px; box-shadow: 0 2px 5px rgba(0,0,0,0.02); }}
                th, td {{ padding: 15px; border: 1px solid #dee2e6; text-align: left; }}
                th {{ background-color: #f1f3f5; font-weight: 600; color: #495057; }}
                .graphs {{ display: flex; gap: 30px; margin-bottom: 30px; flex-wrap: wrap; justify-content: space-between; }}
                .graph-card {{ flex: 1; min-width: 450px; background: #fff; padding: 15px; border-radius: 8px; border: 1px solid #e9ecef; box-shadow: 0 4px 6px rgba(0,0,0,0.02); text-align: center; }}
                .graph-card img {{ max-width: 100%; border-radius: 4px; }}
                .errors {{ background-color: #f8d7da; padding: 25px; border-radius: 8px; border: 1px solid #f5c2c7; }}
                .errors h2 {{ color: #842029; margin-top: 0; }}
                .errors ul {{ padding-left: 20px; color: #842029; }}
                .back-btn {{ display: inline-block; margin-top: 30px; padding: 10px 20px; background: #007acc; color: white; text-decoration: none; border-radius: 5px; transition: background 0.2s; }}
                .back-btn:hover {{ background: #005f9e; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div>
                        <h1>{result.ammeter_type.upper()} Report</h1>
                        <div class="meta-info">
                            <p><strong>Test ID:</strong> {result.test_id}</p>
                            <p><strong>Timestamp:</strong> {formatted_time}</p>
                        </div>
                    </div>
                    <div class="status {result.status.lower()}">{result.status}</div>
                </div>
                
                <h2>Execution Summary</h2>
                <table>
                    <tr>
                        <th>Mode</th>
                        <th>Frequency (Hz)</th>
                        <th>Expected Samples</th>
                        <th>Attempted</th>
                        <th>Successful</th>
                        <th>Failed</th>
                    </tr>
                    <tr>
                        <td>{result.configuration.mode.upper()}</td>
                        <td>{result.configuration.sampling_frequency_hz}</td>
                        <td>{result.expected_samples}</td>
                        <td>{result.attempted_samples}</td>
                        <td>{result.successful_samples}</td>
                        <td>{result.failed_samples}</td>
                    </tr>
                </table>
                
                <h2>Statistical Data</h2>
                <table>
                    <tr>
                        <th>Mean (A)</th>
                        <th>Median (A)</th>
                        <th>Min (A)</th>
                        <th>Max (A)</th>
                        <th>Std Dev (A)</th>
                    </tr>
                    <tr>
                        <td>{stats.get('mean') if stats.get('mean') is not None else 'N/A'}</td>
                        <td>{stats.get('median') if stats.get('median') is not None else 'N/A'}</td>
                        <td>{stats.get('min') if stats.get('min') is not None else 'N/A'}</td>
                        <td>{stats.get('max') if stats.get('max') is not None else 'N/A'}</td>
                        <td>{stats.get('std_dev') if stats.get('std_dev') is not None else 'N/A'}</td>
                    </tr>
                </table>
                
                <h2>Visualizations</h2>
                <div class="graphs">
                    <div class="graph-card">
                        <img src="graphs/time_{result.test_id}.png" alt="Time Series">
                    </div>
                    <div class="graph-card">
                        <img src="graphs/hist_{result.test_id}.png" alt="Histogram">
                    </div>
                </div>
                
                {errors_html}
                
                <a class="back-btn" href="index.html">&larr; Back to Global Dashboard</a>
            </div>
        </body>
        </html>
        """
        
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
            
        DashboardGenerator.generate_global_dashboard(base_dir)
        return html_path

    @staticmethod
    def generate_global_dashboard(base_dir: str = "results/dashboards"):
        index_path = os.path.join(base_dir, "index.html")
        data_dir = "results/data"
        consistency = ConsistencyAnalyzer.analyze_history(data_dir)
        
        runs_data = []
        if os.path.exists(data_dir):
            for file in os.listdir(data_dir):
                if file.endswith(".json"):
                    try:
                        with open(os.path.join(data_dir, file), 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            runs_data.append({
                                'test_id': data.get('test_id'),
                                'timestamp': data.get('timestamp', ''),
                                'formatted_time': format_timestamp(data.get('timestamp', '')),
                                'ammeter_type': data.get('ammeter_type', 'unknown').upper(),
                                'status': data.get('status', 'ERROR'),
                                'successful': data.get('successful_samples', 0),
                                'expected': data.get('expected_samples', 0),
                                'link': f"run_{data.get('test_id')}.html"
                            })
                    except Exception:
                        pass
        
        runs_data.sort(key=lambda x: x['timestamp'], reverse=True)
        
        consistency_html = ""
        for ammeter, cons in consistency.items():
            consistency_html += f"""
            <tr>
                <td><strong>{ammeter.upper()}</strong></td>
                <td>{cons['historical_runs']}</td>
                <td>{round(cons['mean_of_means'], 4) if cons['mean_of_means'] is not None else 'N/A'}</td>
                <td>{round(cons['std_dev_of_means'], 4) if cons['std_dev_of_means'] is not None else 'N/A'}</td>
            </tr>
            """
            
        runs_html = ""
        for r in runs_data:
            status_class = r['status'].lower()
            runs_html += f"""
            <a href="{r['link']}" class="run-card">
                <div class="run-header">
                    <span class="run-title">{r['ammeter_type']}</span>
                    <span class="status-badge {status_class}">{r['status']}</span>
                </div>
                <div class="run-details">
                    <span>📅 {r['formatted_time']}</span>
                    <span>📊 {r['successful']} / {r['expected']} Samples</span>
                    <span class="run-id">ID: {r['test_id'][:8]}...</span>
                </div>
            </a>
            """
            
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Global Ammeter Dashboard</title>
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f8f9fa; color: #212529; margin: 0; padding: 40px; }}
                h1, h2 {{ color: #343a40; }}
                .container {{ max-width: 1100px; margin: 0 auto; background: #fff; padding: 40px; border-radius: 12px; box-shadow: 0 10px 30px rgba(0,0,0,0.05); }}
                .header {{ border-bottom: 1px solid #dee2e6; padding-bottom: 20px; margin-bottom: 30px; }}
                table {{ width: 100%; border-collapse: collapse; margin-bottom: 40px; box-shadow: 0 2px 5px rgba(0,0,0,0.02); }}
                th, td {{ padding: 15px; border: 1px solid #dee2e6; text-align: left; }}
                th {{ background-color: #f1f3f5; font-weight: 600; color: #495057; }}
                tr:hover {{ background-color: #f8f9fa; }}
                
                .runs-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 20px; }}
                .run-card {{ display: block; background: #ffffff; border: 1px solid #dee2e6; border-radius: 10px; padding: 20px; text-decoration: none; color: inherit; transition: all 0.3s ease; box-shadow: 0 2px 4px rgba(0,0,0,0.02); }}
                .run-card:hover {{ transform: translateY(-5px); box-shadow: 0 8px 15px rgba(0,0,0,0.08); border-color: #007acc; }}
                .run-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; }}
                .run-title {{ font-size: 18px; font-weight: bold; color: #2c3e50; }}
                .status-badge {{ padding: 5px 12px; border-radius: 20px; font-size: 12px; font-weight: bold; letter-spacing: 0.5px; }}
                .status-badge.pass {{ background-color: #d1e7dd; color: #0f5132; }}
                .status-badge.fail {{ background-color: #f8d7da; color: #842029; }}
                .status-badge.error {{ background-color: #fff3cd; color: #664d03; }}
                .run-details {{ display: flex; flex-direction: column; gap: 8px; font-size: 14px; color: #6c757d; }}
                .run-id {{ font-family: monospace; color: #adb5bd; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Global Ammeter Testing Dashboard</h1>
                    <p style="color: #6c757d;">Automated testing framework history and consistency tracking.</p>
                </div>
                
                <h2>Relative Consistency Analysis</h2>
                <table>
                    <tr>
                        <th>Ammeter Type</th>
                        <th>Historical Runs</th>
                        <th>Mean of Means (A)</th>
                        <th>Std Dev of Means (A)</th>
                    </tr>
                    {consistency_html}
                </table>
                
                <h2>Recent Test Runs</h2>
                <div class="runs-grid">
                    {runs_html}
                </div>
            </div>
        </body>
        </html>
        """
        
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
