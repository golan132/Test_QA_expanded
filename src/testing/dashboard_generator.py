import os
import json
import matplotlib
matplotlib.use('Agg') # Headless backend
import matplotlib.pyplot as plt
from datetime import datetime
from typing import List
from src.testing.types import TestRunResult
from src.testing.consistency_analyzer import ConsistencyAnalyzer
from src.testing.dashboard_templates import REPORT_TEMPLATE, GLOBAL_DASHBOARD_TEMPLATE

def format_timestamp(ts: str) -> str:
    try:
        dt = datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ")
        return dt.strftime("%d/%m/%Y %H:%M:%S")
    except Exception:
        return ts

class DashboardGenerator:
    @staticmethod
    def generate_dashboard(result: TestRunResult, target_dir: str) -> str:
        # In the new architecture, target_dir is already fully qualified: results/runs/YYYY-MM-DD/{ammeter}_{short_id}/
        # Everything (json, html, png) goes directly into this flat folder.
        
        timestamps = []
        values = []
        for i, m in enumerate(result.measurements):
            if m.success and m.value is not None:
                timestamps.append(i) # using index as simplified time axis
                values.append(m.value)
                
        time_series_path = os.path.join(target_dir, "time_series.png")
        plt.figure(figsize=(8, 4))
        plt.plot(timestamps, values, marker='o', linestyle='-', color='#007acc', linewidth=2)
        plt.title(f"{result.ammeter_type.upper()} - Current over Time", fontsize=14)
        plt.xlabel("Sample Index", fontsize=12)
        plt.ylabel("Current (A)", fontsize=12)
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.tight_layout()
        plt.savefig(time_series_path)
        plt.close()
        
        hist_path = os.path.join(target_dir, "histogram.png")
        plt.figure(figsize=(8, 4))
        plt.hist(values, bins=10, color='#28a745', edgecolor='black', alpha=0.7)
        plt.title(f"{result.ammeter_type.upper()} - Value Distribution", fontsize=14)
        plt.xlabel("Current (A)", fontsize=12)
        plt.ylabel("Frequency", fontsize=12)
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.tight_layout()
        plt.savefig(hist_path)
        plt.close()
        
        html_path = os.path.join(target_dir, "report.html")
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
        
        # Calculate relative path to project root
        root_path = "../../../../index.html"
        
        # We need to overwrite the template slightly to point to the correct image paths
        # Since images are now in the same directory, we don't use graphs/time...
        custom_report = REPORT_TEMPLATE.replace("graphs/time_{test_id}.png", "time_series.png")
        custom_report = custom_report.replace("graphs/hist_{test_id}.png", "histogram.png")
        
        html_content = custom_report.format(
            ammeter_type=result.ammeter_type.upper(),
            test_id=result.test_id,
            formatted_time=formatted_time,
            status_class=result.status.lower(),
            status=result.status,
            mode=result.configuration.mode.upper(),
            frequency=result.configuration.sampling_frequency_hz,
            expected_samples=result.expected_samples,
            attempted_samples=result.attempted_samples,
            successful_samples=result.successful_samples,
            failed_samples=result.failed_samples,
            mean=stats.get('mean') if stats.get('mean') is not None else 'N/A',
            median=stats.get('median') if stats.get('median') is not None else 'N/A',
            min_val=stats.get('min') if stats.get('min') is not None else 'N/A',
            max_val=stats.get('max') if stats.get('max') is not None else 'N/A',
            std_dev=stats.get('std_dev') if stats.get('std_dev') is not None else 'N/A',
            errors_html=errors_html,
            root_path=root_path
        )
        
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
            
        DashboardGenerator.generate_global_dashboard()
        return html_path

    @staticmethod
    def generate_global_dashboard():
        index_path = "index.html"
        runs_dir = "results/runs"
        consistency = ConsistencyAnalyzer.analyze_history(runs_dir)
        
        runs_data = []
        if os.path.exists(runs_dir):
            for root, _, files in os.walk(runs_dir):
                for file in files:
                    if file == "data.json":
                        try:
                            with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                                data = json.load(f)
                                
                                html_rel_path = os.path.join(root, "report.html").replace(chr(92), "/")
                                
                                if os.path.exists(os.path.join(root, "report.html")):
                                    runs_data.append({
                                        'test_id': data.get('test_id'),
                                        'timestamp': data.get('timestamp', ''),
                                        'formatted_time': format_timestamp(data.get('timestamp', '')),
                                        'ammeter_type': data.get('ammeter_type', 'unknown').upper(),
                                        'status': data.get('status', 'ERROR'),
                                        'successful': data.get('successful_samples', 0),
                                        'expected': data.get('expected_samples', 0),
                                        'link': html_rel_path,
                                        'raw_date': data.get('timestamp', '')
                                    })
                        except Exception:
                            pass
        
        runs_data.sort(key=lambda x: x['timestamp'], reverse=True)
        
        # --- Generate Global Graphs ---
        global_graphs_dir = "results/global_graphs"
        os.makedirs(global_graphs_dir, exist_ok=True)
        
        has_graphs = False
        if runs_data:
            has_graphs = True
            
            # 1. Status Distribution (Pie Chart)
            statuses = [r['status'] for r in runs_data]
            status_counts = {s: statuses.count(s) for s in set(statuses)}
            plt.figure(figsize=(6, 4))
            colors = {'PASS': '#28a745', 'FAIL': '#dc3545', 'ERROR': '#ffc107'}
            pie_colors = [colors.get(s, '#6c757d') for s in status_counts.keys()]
            plt.pie(status_counts.values(), labels=status_counts.keys(), colors=pie_colors, autopct='%1.1f%%', startangle=90)
            plt.title("Overall Run Status Distribution")
            plt.tight_layout()
            plt.savefig(os.path.join(global_graphs_dir, "status_pie.png"))
            plt.close()
            
            # 2. Pass Rate by Ammeter Type (Bar Chart)
            ammeter_types = list(set([r['ammeter_type'] for r in runs_data]))
            pass_rates = []
            for am in ammeter_types:
                am_runs = [r for r in runs_data if r['ammeter_type'] == am]
                passed = len([r for r in am_runs if r['status'] == 'PASS'])
                pass_rates.append((passed / len(am_runs)) * 100 if len(am_runs) > 0 else 0)
                
            plt.figure(figsize=(6, 4))
            bars = plt.bar(ammeter_types, pass_rates, color='#007acc')
            plt.title("Pass Rate by Ammeter Type (%)")
            plt.ylim(0, 110)
            for bar in bars:
                yval = bar.get_height()
                plt.text(bar.get_x() + bar.get_width()/2.0, yval + 1, f'{yval:.1f}%', ha='center', va='bottom')
            plt.tight_layout()
            plt.savefig(os.path.join(global_graphs_dir, "ammeter_pass_rates.png"))
            plt.close()
            
        graphs_html = ""
        if has_graphs:
            graphs_html = f"""
            <h2>Global Statistics</h2>
            <div class="global-stats">
                <div class="graph-card">
                    <img src="results/global_graphs/status_pie.png" alt="Status Distribution">
                </div>
                <div class="graph-card">
                    <img src="results/global_graphs/ammeter_pass_rates.png" alt="Pass Rates">
                </div>
            </div>
            """
        
        # --- End Global Graphs ---
        
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
            pass_rate_float = (r['successful'] / r['expected'] * 100) if r['expected'] > 0 else 0
            pass_rate = f"{pass_rate_float:.1f}%"
            runs_html += f"""
            <tr>
                <td data-sort="{r['raw_date']}">{r['formatted_time']}</td>
                <td data-sort="{r['ammeter_type']}">{r['ammeter_type']}</td>
                <td data-sort="{r['expected']}">{r['expected']}</td>
                <td data-sort="{r['successful']}">{r['successful']}</td>
                <td data-sort="{pass_rate_float}">{pass_rate}</td>
                <td data-sort="{r['status']}"><span class="status-badge {status_class}">{r['status']}</span></td>
                <td><a href="{r['link']}" class="view-link">View Report</a></td>
            </tr>
            """
            
        html_content = GLOBAL_DASHBOARD_TEMPLATE.format(
            graphs_html=graphs_html,
            consistency_html=consistency_html,
            runs_html=runs_html
        )
        
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
