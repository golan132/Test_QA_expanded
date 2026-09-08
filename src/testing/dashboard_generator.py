import os
import json
from datetime import datetime
from typing import Optional
from src.testing.types import TestRunResult, Configuration
from src.testing.consistency_analyzer import ConsistencyAnalyzer


def format_timestamp(ts: str) -> str:
    try:
        dt = datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ")
        return dt.strftime("%d/%m/%Y %H:%M:%S")
    except Exception:
        return ts


class DashboardGenerator:
    @staticmethod
    def generate_dashboard(
        result: TestRunResult, target_dir: str, config: Optional[Configuration] = None
    ) -> str:
        try:
            config.plot_types if config else ["time_series", "histogram"]
            config.visualizations_enabled if config else True
            config.result_base_dir if config else "results/runs"

            timestamps = []
            values = []
            for i, m in enumerate(result.measurements):
                if m.success and m.value is not None:
                    timestamps.append(i)
                    values.append(m.value)

            # Visualizations are now handled client-side using Chart.js

            # Removed individual report.html generation to support SPA dashboard architecture

            DashboardGenerator.generate_global_dashboard(config)
            return target_dir

        except Exception as e:
            print(f"Warning: Failed to generate dashboard for {result.test_id}: {e}")
            return ""

    @staticmethod
    def generate_global_dashboard(config: Optional[Configuration] = None):
        try:
            plot_types = (
                config.plot_types
                if config
                else ["global_pie_chart", "global_bar_chart"]
            )
            config.visualizations_enabled if config else True
            runs_dir = config.result_base_dir if config else "results/runs"

            index_path = "index.html"
            consistency = ConsistencyAnalyzer.analyze_history(runs_dir)

            runs_data = []
            if os.path.exists(runs_dir):
                for root, _, files in os.walk(runs_dir):
                    for file in files:
                        if file == "data.json":
                            try:
                                with open(
                                    os.path.join(root, file), "r", encoding="utf-8"
                                ) as f:
                                    data = json.load(f)
                                    # Capture the whole data to use in SPA
                                    run_obj = data
                                    run_obj["formatted_time"] = format_timestamp(
                                        data.get("timestamp", "")
                                    )

                                    # Calculate relative run directory for loading graphs
                                    html_rel_path = root.replace(chr(92), "/")
                                    run_obj["run_dir"] = html_rel_path

                                    runs_data.append(run_obj)
                            except Exception:
                                pass

            runs_data.sort(key=lambda x: x["timestamp"], reverse=True)

            # Global graphs are now handled client-side by Chart.js

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
            for i, r in enumerate(runs_data):
                status = r.get("status", "ERROR")
                status_class = status.lower()
                expected = r.get("expected_samples", 0)
                successful = r.get("successful_samples", 0)

                pass_rate_float = (successful / expected * 100) if expected > 0 else 0
                pass_rate = f"{pass_rate_float:.1f}%"

                runs_html += f"""
                <tr>
                    <td data-sort="{r.get('timestamp', '')}">{r.get('formatted_time', '')}</td>
                    <td data-sort="{r.get('ammeter_type', '')}">{r.get('ammeter_type', '').upper()}</td>
                    <td data-sort="{expected}">{expected}</td>
                    <td data-sort="{successful}">{successful}</td>
                    <td data-sort="{pass_rate_float}">{pass_rate}</td>
                    <td data-sort="{status}"><span class="status-badge {status_class}">{status}</span></td>
                    <td><button onclick="showDetail({i})" class="view-link">View Report</button></td>
                </tr>
                """

            best_ammeter_verdict = ConsistencyAnalyzer.get_most_reliable_ammeter(
                consistency
            )

            # Load and format accuracy assessment template
            templates_dir = os.path.join(os.path.dirname(__file__), "..", "templates")
            with open(
                os.path.join(templates_dir, "accuracy_assessment.html"),
                "r",
                encoding="utf-8",
            ) as f:
                accuracy_template = f.read()
            accuracy_assessment_html = accuracy_template.format(
                best_ammeter_verdict=best_ammeter_verdict
            )

            # Load CSS
            with open(
                os.path.join(templates_dir, "dashboard.css"), "r", encoding="utf-8"
            ) as f:
                css_content = f.read()

            # Load and format JS
            js_dir = os.path.join(templates_dir, "js")
            js_files = [
                "state.js",
                "utils.js",
                "ui.js",
                "charts_global.js",
                "charts_analytics.js",
                "main.js",
            ]
            js_content = ""
            for js_file in js_files:
                with open(os.path.join(js_dir, js_file), "r", encoding="utf-8") as f:
                    js_content += f.read() + "\n\n"
            js_content = js_content.replace("__ALL_RUNS_JSON__", json.dumps(runs_data))

            # Load and format index template
            with open(
                os.path.join(templates_dir, "index.html"), "r", encoding="utf-8"
            ) as f:
                index_template = f.read()

            html_content = index_template.format(
                css_content=css_content,
                js_content=js_content,
                consistency_html=consistency_html,
                runs_html=runs_html,
                accuracy_assessment_html=accuracy_assessment_html,
            )

            with open(index_path, "w", encoding="utf-8") as f:
                f.write(html_content)

        except Exception as e:
            print(f"Warning: Failed to generate global dashboard: {e}")
