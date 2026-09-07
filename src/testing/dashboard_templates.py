REPORT_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Test Report - {test_id}</title>
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
                <h1>{ammeter_type} Report</h1>
                <div class="meta-info">
                    <p><strong>Test ID:</strong> {test_id}</p>
                    <p><strong>Timestamp:</strong> {formatted_time}</p>
                </div>
            </div>
            <div class="status {status_class}">{status}</div>
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
                <td>{mode}</td>
                <td>{frequency}</td>
                <td>{expected_samples}</td>
                <td>{attempted_samples}</td>
                <td>{successful_samples}</td>
                <td>{failed_samples}</td>
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
                <td>{mean}</td>
                <td>{median}</td>
                <td>{min_val}</td>
                <td>{max_val}</td>
                <td>{std_dev}</td>
            </tr>
        </table>
        
        <h2>Visualizations</h2>
        <div class="graphs">
            <div class="graph-card">
                <img src="graphs/time_{test_id}.png" alt="Time Series">
            </div>
            <div class="graph-card">
                <img src="graphs/hist_{test_id}.png" alt="Histogram">
            </div>
        </div>
        
        {errors_html}
        
        <a class="back-btn" href="{root_path}">&larr; Back to Global Dashboard</a>
    </div>
</body>
</html>
"""

GLOBAL_DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Global Ammeter Dashboard</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f8f9fa; color: #212529; margin: 0; padding: 40px; }}
        h1, h2 {{ color: #343a40; margin-bottom: 20px; }}
        .container {{ max-width: 1100px; margin: 0 auto; background: #fff; padding: 40px; border-radius: 4px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border: 1px solid #dee2e6; }}
        .header {{ border-bottom: 2px solid #343a40; padding-bottom: 10px; margin-bottom: 30px; }}
        table {{ width: 100%; border-collapse: collapse; margin-bottom: 50px; font-size: 14px; }}
        th, td {{ padding: 12px 15px; border: 1px solid #dee2e6; text-align: left; }}
        th {{ background-color: #e9ecef; font-weight: 600; color: #495057; text-transform: uppercase; font-size: 12px; letter-spacing: 0.5px; cursor: pointer; user-select: none; }}
        th:hover {{ background-color: #dee2e6; }}
        tr:hover {{ background-color: #f1f3f5; }}
        
        .status-badge {{ padding: 4px 8px; border-radius: 3px; font-size: 12px; font-weight: bold; letter-spacing: 0.5px; display: inline-block; text-align: center; min-width: 60px; }}
        .status-badge.pass {{ background-color: #d1e7dd; color: #0f5132; border: 1px solid #badbcc; }}
        .status-badge.fail {{ background-color: #f8d7da; color: #842029; border: 1px solid #f5c2c7; }}
        .status-badge.error {{ background-color: #fff3cd; color: #664d03; border: 1px solid #ffecb5; }}
        
        .view-link {{ color: #0d6efd; text-decoration: none; font-weight: 500; }}
        .view-link:hover {{ text-decoration: underline; color: #0a58ca; }}
        
        .sort-icon {{ font-size: 14px; margin-left: 5px; color: #6c757d; font-weight: bold; }}
        
        .global-stats {{ display: flex; gap: 20px; margin-bottom: 40px; justify-content: center; flex-wrap: wrap; }}
        .graph-card {{ flex: 1; min-width: 400px; background: #fff; padding: 15px; border-radius: 8px; border: 1px solid #dee2e6; box-shadow: 0 2px 4px rgba(0,0,0,0.02); text-align: center; }}
        .graph-card img {{ max-width: 100%; border-radius: 4px; }}
    </style>
    <script>
        function sortTable(n, tableId) {{
            var table, rows, switching, i, x, y, shouldSwitch, dir, switchcount = 0;
            table = document.getElementById(tableId);
            switching = true;
            dir = "asc"; 
            
            while (switching) {{
                switching = false;
                rows = table.getElementsByTagName("TR");
                for (i = 1; i < (rows.length - 1); i++) {{
                    shouldSwitch = false;
                    
                    var tdX = rows[i].getElementsByTagName("TD");
                    var tdY = rows[i + 1].getElementsByTagName("TD");
                    if (tdX.length <= n || tdY.length <= n) continue;
                    
                    x = tdX[n];
                    y = tdY[n];
                    
                    var xVal = x.getAttribute("data-sort") || x.innerText;
                    var yVal = y.getAttribute("data-sort") || y.innerText;
                    
                    var xNum = parseFloat(xVal);
                    var yNum = parseFloat(yVal);
                    
                    if (!isNaN(xNum) && !isNaN(yNum)) {{
                        xVal = xNum;
                        yVal = yNum;
                    }} else {{
                        xVal = xVal.toLowerCase();
                        yVal = yVal.toLowerCase();
                    }}
                    
                    if (dir == "asc") {{
                        if (xVal > yVal) {{
                            shouldSwitch = true;
                            break;
                        }}
                    }} else if (dir == "desc") {{
                        if (xVal < yVal) {{
                            shouldSwitch = true;
                            break;
                        }}
                    }}
                }}
                if (shouldSwitch) {{
                    rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
                    switching = true;
                    switchcount ++; 
                }} else {{
                    if (switchcount == 0 && dir == "asc") {{
                        dir = "desc";
                        switching = true;
                    }}
                }}
            }}
            
            // Update arrows
            var headers = table.rows[0].getElementsByTagName("TH");
            for (var j = 0; j < headers.length; j++) {{
                var icon = headers[j].querySelector(".sort-icon");
                if (icon) icon.innerHTML = "↕";
            }}
            var activeIcon = headers[n].querySelector(".sort-icon");
            if (activeIcon) {{
                activeIcon.innerHTML = (dir === "asc") ? "↑" : "↓";
                activeIcon.style.color = "#000";
            }}
        }}
    </script>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Test QA Framework - Global Dashboard</h1>
            <p style="color: #6c757d; font-size: 14px;">Automated measurement history and consistency tracking.</p>
        </div>
        
        {graphs_html}
        
        <h2>Relative Consistency Analysis</h2>
        <table id="consistencyTable">
            <thead>
                <tr>
                    <th onclick="sortTable(0, 'consistencyTable')">Ammeter Type <span class="sort-icon">↕</span></th>
                    <th onclick="sortTable(1, 'consistencyTable')">Historical Runs <span class="sort-icon">↕</span></th>
                    <th onclick="sortTable(2, 'consistencyTable')">Mean of Means (A) <span class="sort-icon">↕</span></th>
                    <th onclick="sortTable(3, 'consistencyTable')">Std Dev of Means (A) <span class="sort-icon">↕</span></th>
                </tr>
            </thead>
            <tbody>
                {consistency_html}
            </tbody>
        </table>
        
        <h2>Recent Execution History</h2>
        <table id="runsTable">
            <thead>
                <tr>
                    <th onclick="sortTable(0, 'runsTable')">Timestamp <span class="sort-icon">↕</span></th>
                    <th onclick="sortTable(1, 'runsTable')">Ammeter Type <span class="sort-icon">↕</span></th>
                    <th onclick="sortTable(2, 'runsTable')">Expected Samples <span class="sort-icon">↕</span></th>
                    <th onclick="sortTable(3, 'runsTable')">Successful Samples <span class="sort-icon">↕</span></th>
                    <th onclick="sortTable(4, 'runsTable')">Pass Rate <span class="sort-icon">↕</span></th>
                    <th onclick="sortTable(5, 'runsTable')">Status <span class="sort-icon">↕</span></th>
                    <th>Action</th>
                </tr>
            </thead>
            <tbody>
                {runs_html}
            </tbody>
        </table>
    </div>
</body>
</html>
"""
