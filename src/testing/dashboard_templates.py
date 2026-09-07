GLOBAL_DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Global Ammeter Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f0f2f5; color: #212529; margin: 0; padding: 0; padding-top: 80px; }}
        h1, h2, h3 {{ color: #343a40; margin-bottom: 20px; }}
        
        /* Navbar */
        .navbar {{ position: fixed; top: 0; left: 0; width: 100%; height: 64px; background-color: #1a1d23; display: flex; align-items: center; padding: 0 40px; box-sizing: border-box; z-index: 50; border-bottom-left-radius: 16px; border-bottom-right-radius: 16px; box-shadow: 0 4px 20px rgba(0,0,0,0.15); }}
        .navbar-brand {{ color: #fff; font-size: 18px; font-weight: bold; margin-right: 40px; }}
        .nav-btn {{ background: transparent; border: none; color: #9ca3af; font-size: 14px; padding: 10px 22px; cursor: pointer; border-radius: 8px; transition: all 0.2s ease; font-weight: 600; }}
        .nav-btn:hover {{ color: #fff; background-color: rgba(255,255,255,0.08); }}
        .nav-btn.active {{ color: #fff; background-color: #3b82f6; box-shadow: 0 2px 8px rgba(59,130,246,0.3); }}
        
        .tab-content {{ display: none; padding: 40px; max-width: 1200px; margin: 0 auto; }}
        .tab-content.active {{ display: block; }}
        
        .container {{ background: #fff; padding: 40px; border-radius: 16px; box-shadow: 0 8px 24px rgba(0,0,0,0.06); border: 1px solid #e5e7eb; margin-bottom: 30px; transition: box-shadow 0.25s ease; }}
        .container:hover {{ box-shadow: 0 12px 32px rgba(0,0,0,0.09); }}
        
        table {{ width: 100%; border-collapse: collapse; margin-bottom: 30px; font-size: 14px; }}
        th, td {{ padding: 12px 15px; border: 1px solid #e5e7eb; text-align: left; }}
        th {{ background-color: #f9fafb; font-weight: 600; color: #495057; text-transform: uppercase; font-size: 12px; letter-spacing: 0.5px; cursor: pointer; user-select: none; }}
        th:hover {{ background-color: #f3f4f6; }}
        tr:hover {{ background-color: #f9fafb; }}
        .status-badge {{ padding: 5px 10px; border-radius: 6px; font-size: 12px; font-weight: bold; letter-spacing: 0.5px; display: inline-block; text-align: center; min-width: 60px; }}
        .status-badge.pass {{ background-color: #d1fae5; color: #065f46; }}
        .status-badge.fail {{ background-color: #fee2e2; color: #991b1b; }}
        .status-badge.error {{ background-color: #fef3c7; color: #92400e; }}
        .status-badge.partial {{ background-color: #e0f2fe; color: #075985; }}
        
        .view-link {{ color: #3b82f6; text-decoration: none; font-weight: 500; cursor: pointer; background: none; border: none; padding: 0; }}
        .view-link:hover {{ text-decoration: underline; color: #2563eb; }}
        .sort-icon {{ font-size: 14px; margin-left: 5px; color: #9ca3af; font-weight: bold; }}
        
        .grid-2 {{ display: grid; grid-template-columns: 1fr 1fr; gap: 24px; margin-bottom: 30px; }}
        .graph-card {{ background: #fff; padding: 20px; border-radius: 16px; border: 1px solid #e5e7eb; box-shadow: 0 6px 18px rgba(0,0,0,0.04); position: relative; height: 350px; transition: box-shadow 0.25s ease, transform 0.25s ease; }}
        .graph-card:hover {{ box-shadow: 0 10px 28px rgba(0,0,0,0.08); transform: translateY(-2px); }}
        .home-graph {{ height: 240px; }}
        
        /* Modal */
        .detail-overlay {{ display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.45); z-index: 100; }}
        .detail-panel {{ display: none; position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); background: #fff; border-radius: 20px; box-shadow: 0 25px 60px rgba(0,0,0,0.2); max-width: 1000px; width: 90%; max-height: 85vh; overflow-y: auto; z-index: 101; padding: 40px; }}
        .detail-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 25px; padding-bottom: 15px; border-bottom: 1px solid #e5e7eb; }}
        .detail-close {{ background: #f3f4f6; border: none; font-size: 18px; cursor: pointer; padding: 6px 12px; border-radius: 8px; color: #6b7280; transition: 0.2s; }}
        .detail-close:hover {{ background-color: #e5e7eb; color: #111827; }}
        .full-width-graph {{ width: 100%; height: 300px; margin-top: 20px; }}
        .detail-errors {{ background-color: #fef2f2; padding: 20px; border-radius: 12px; border: 1px solid #fecaca; margin-top: 20px; }}
    </style>
    <script>
        var ALL_RUNS = {all_runs_json};
        var currentDetailCharts = [];
        var globalCharts = [];
        var analyticsCharts = [];

        function destroyCharts(chartArray) {{
            chartArray.forEach(function(c) {{ c.destroy(); }});
            chartArray.length = 0;
        }}

        function switchTab(tabId) {{
            document.querySelectorAll('.tab-content').forEach(function(el) {{ el.classList.remove('active'); }});
            document.querySelectorAll('.nav-btn').forEach(function(el) {{ el.classList.remove('active'); }});
            
            document.getElementById('tab-' + tabId).classList.add('active');
            document.getElementById('btn-' + tabId).classList.add('active');
            
            if (tabId === 'analytics' && analyticsCharts.length === 0) {{
                initAnalyticsCharts();
            }}
        }}

        function initGlobalCharts() {{
            if (!ALL_RUNS || ALL_RUNS.length === 0) return;
            
            var statusCounts = {{ 'PASS': 0, 'FAIL': 0, 'ERROR': 0, 'PARTIAL': 0 }};
            var ammeterTypes = {{}};
            
            ALL_RUNS.forEach(function(run) {{
                var s = run.status.toUpperCase();
                if (statusCounts[s] !== undefined) statusCounts[s]++;
                else statusCounts[s] = 1;
                
                var am = run.ammeter_type;
                if (!ammeterTypes[am]) ammeterTypes[am] = {{ pass: 0, total: 0 }};
                ammeterTypes[am].total++;
                if (s === 'PASS') ammeterTypes[am].pass++;
            }});
            
            var pieColors = {{ 'PASS': '#28a745', 'FAIL': '#dc3545', 'ERROR': '#ffc107', 'PARTIAL': '#0dcaf0' }};
            var pieLabels = Object.keys(statusCounts).filter(k => statusCounts[k] > 0);
            var pieData = pieLabels.map(k => statusCounts[k]);
            var pieBgColors = pieLabels.map(k => pieColors[k] || '#6c757d');
            
            var ctxPie = document.getElementById('globalPieChart').getContext('2d');
            globalCharts.push(new Chart(ctxPie, {{
                type: 'doughnut',
                data: {{ labels: pieLabels, datasets: [{{ data: pieData, backgroundColor: pieBgColors, borderWidth: 0, hoverOffset: 6 }}] }},
                options: {{ responsive: true, maintainAspectRatio: false, cutout: '60%', plugins: {{ title: {{ display: true, text: 'Overall Run Status Distribution' }} }} }}
            }}));
            
            var amLabels = Object.keys(ammeterTypes);
            var amData = amLabels.map(k => (ammeterTypes[k].pass / ammeterTypes[k].total) * 100);
            
            var ctxBar = document.getElementById('globalBarChart').getContext('2d');
            globalCharts.push(new Chart(ctxBar, {{
                type: 'bar',
                data: {{ labels: amLabels, datasets: [{{ label: 'Pass Rate (%)', data: amData, backgroundColor: '#3b82f6', borderRadius: 6, barPercentage: 0.5 }}] }},
                options: {{ 
                    responsive: true, maintainAspectRatio: false, 
                    plugins: {{ title: {{ display: true, text: 'Pass Rate by Ammeter Type (%)' }}, legend: {{display: false}} }},
                    scales: {{ y: {{ min: 0, max: 100, grid: {{ color: '#f3f4f6' }} }}, x: {{ grid: {{ display: false }} }} }}
                }}
            }}));
        }}

        function initAnalyticsCharts() {{
            if (!ALL_RUNS || ALL_RUNS.length === 0) return;
            
            // Reverse so oldest is first
            var chronologicalRuns = [...ALL_RUNS].reverse();
            
            var timeLabels = [];
            var passRateData = [];
            
            var ammeterMeans = {{}};
            var errorTypes = {{}};
            var volumeByDate = {{}};
            
            chronologicalRuns.forEach(function(run) {{
                var label = run.formatted_time;
                timeLabels.push(label);
                
                // Pass Rate
                var pr = (run.expected_samples > 0) ? (run.successful_samples / run.expected_samples) * 100 : 0;
                passRateData.push(pr);
                
                // Mean Stability
                var am = run.ammeter_type;
                if (!ammeterMeans[am]) ammeterMeans[am] = [];
                // Pad previous missing points with null
                while(ammeterMeans[am].length < timeLabels.length - 1) ammeterMeans[am].push(null);
                ammeterMeans[am].push(run.statistics ? run.statistics.mean : null);
                
                // Volume
                var d = label.split(' ')[0];
                if (!volumeByDate[d]) volumeByDate[d] = 0;
                volumeByDate[d] += run.attempted_samples;
                
                // Errors
                if (run.errors) {{
                    run.errors.forEach(function(e) {{
                        var t = e.error_type || 'Unknown';
                        if (!errorTypes[t]) errorTypes[t] = 0;
                        errorTypes[t]++;
                    }});
                }}
            }});
            
            // Pad all ammeter means to the end
            Object.keys(ammeterMeans).forEach(k => {{
                while(ammeterMeans[k].length < timeLabels.length) ammeterMeans[k].push(null);
            }});
            
            // 1. Pass Rate Trend
            var ctxPass = document.getElementById('chartPassRateTrend').getContext('2d');
            var gradPass = ctxPass.createLinearGradient(0, 0, 0, 300);
            gradPass.addColorStop(0, 'rgba(16, 185, 129, 0.3)');
            gradPass.addColorStop(1, 'rgba(16, 185, 129, 0.0)');
            analyticsCharts.push(new Chart(ctxPass, {{
                type: 'line',
                data: {{ labels: timeLabels, datasets: [{{ label: 'Pass Rate (%)', data: passRateData, borderColor: '#10b981', backgroundColor: gradPass, fill: true, tension: 0.4, borderWidth: 2.5, pointRadius: 3, pointHoverRadius: 6 }}] }},
                options: {{ responsive: true, maintainAspectRatio: false, plugins: {{ title: {{ display: true, text: 'System Stability (Pass Rate Trend)' }} }}, scales: {{ y: {{ min: 0, max: 100, grid: {{ color: '#f3f4f6' }} }}, x: {{ grid: {{ display: false }}, ticks: {{ maxTicksLimit: 8 }} }} }} }}
            }}));
            
            // 2. Mean Stability
            var meanDatasets = [];
            var colors = ['#3b82f6', '#ef4444', '#f59e0b', '#8b5cf6', '#14b8a6'];
            Object.keys(ammeterMeans).forEach((k, i) => {{
                meanDatasets.push({{
                    label: k.toUpperCase(),
                    data: ammeterMeans[k],
                    borderColor: colors[i % colors.length],
                    spanGaps: true,
                    tension: 0.35,
                    borderWidth: 2.5,
                    pointRadius: 3,
                    pointHoverRadius: 6
                }});
            }});
            var ctxMean = document.getElementById('chartMeanStability').getContext('2d');
            analyticsCharts.push(new Chart(ctxMean, {{
                type: 'line',
                data: {{ labels: timeLabels, datasets: meanDatasets }},
                options: {{ responsive: true, maintainAspectRatio: false, plugins: {{ title: {{ display: true, text: 'Mean Current (A) Stability' }} }}, scales: {{ y: {{ grid: {{ color: '#f3f4f6' }} }}, x: {{ grid: {{ display: false }}, ticks: {{ maxTicksLimit: 8 }} }} }} }}
            }}));
            
            // 3. Error Distribution
            var errLabels = Object.keys(errorTypes);
            var errData = errLabels.map(k => errorTypes[k]);
            var ctxErr = document.getElementById('chartErrorDist').getContext('2d');
            if (errLabels.length > 0) {{
                analyticsCharts.push(new Chart(ctxErr, {{
                    type: 'doughnut',
                    data: {{ labels: errLabels, datasets: [{{ data: errData, backgroundColor: colors, borderWidth: 0, hoverOffset: 6 }}] }},
                    options: {{ responsive: true, maintainAspectRatio: false, cutout: '55%', plugins: {{ title: {{ display: true, text: 'Error Type Distribution' }} }} }}
                }}));
            }} else {{
                // No errors
                var noErrCtx = ctxErr;
                noErrCtx.font = "14px Arial";
                noErrCtx.textAlign = "center";
                noErrCtx.fillText("No Errors Recorded", ctxErr.canvas.width/2, ctxErr.canvas.height/2);
            }}
            
            // 4. Execution Volume
            var volLabels = Object.keys(volumeByDate);
            var volData = volLabels.map(k => volumeByDate[k]);
            var ctxVol = document.getElementById('chartVolume').getContext('2d');
            analyticsCharts.push(new Chart(ctxVol, {{
                type: 'bar',
                data: {{ labels: volLabels, datasets: [{{ label: 'Attempted Samples', data: volData, backgroundColor: '#06b6d4', borderRadius: 6, barPercentage: 0.5 }}] }},
                options: {{ responsive: true, maintainAspectRatio: false, plugins: {{ title: {{ display: true, text: 'Testing Volume by Date' }} }}, scales: {{ y: {{ beginAtZero: true, grid: {{ color: '#f3f4f6' }} }}, x: {{ grid: {{ display: false }} }} }} }}
            }}));
        }}

        function drawHistogram(canvasId, values) {{
            if (values.length === 0) return null;
            var min = Math.min(...values);
            var max = Math.max(...values);
            var bins = 10;
            var binSize = (max - min) / bins || 1;
            
            var counts = new Array(bins).fill(0);
            values.forEach(function(v) {{
                var idx = Math.floor((v - min) / binSize);
                if (idx >= bins) idx = bins - 1;
                counts[idx]++;
            }});
            
            var labels = [];
            for (var i = 0; i < bins; i++) {{
                var b1 = min + (i * binSize);
                var b2 = min + ((i + 1) * binSize);
                labels.push(b1.toFixed(3) + ' - ' + b2.toFixed(3));
            }}
            
            var ctx = document.getElementById(canvasId).getContext('2d');
            return new Chart(ctx, {{
                type: 'bar',
                data: {{ labels: labels, datasets: [{{ label: 'Frequency', data: counts, backgroundColor: 'rgba(139, 92, 246, 0.6)', borderColor: '#8b5cf6', borderWidth: 1, borderRadius: 4 }}] }},
                options: {{ responsive: true, maintainAspectRatio: false, plugins: {{ title: {{ display: true, text: 'Value Distribution' }} }}, scales: {{ y: {{ beginAtZero: true, grid: {{ color: '#f3f4f6' }} }}, x: {{ grid: {{ display: false }}, ticks: {{ display: false }} }} }} }}
            }});
        }}

        function showDetail(index) {{
            var run = ALL_RUNS[index];
            if (!run) return;
            document.getElementById('detailTitle').textContent = run.ammeter_type.toUpperCase() + ' Report';
            document.getElementById('detailTestId').textContent = run.test_id;
            document.getElementById('detailTimestamp').textContent = run.formatted_time;
            var statusEl = document.getElementById('detailStatus');
            statusEl.textContent = run.status;
            statusEl.className = 'status-badge ' + run.status.toLowerCase();
            document.getElementById('detailMode').textContent = run.configuration ? run.configuration.mode.toUpperCase() : 'N/A';
            document.getElementById('detailFrequency').textContent = run.configuration ? run.configuration.sampling_frequency_hz : 'N/A';
            document.getElementById('detailExpected').textContent = run.expected_samples;
            document.getElementById('detailAttempted').textContent = run.attempted_samples;
            document.getElementById('detailSuccessful').textContent = run.successful_samples;
            document.getElementById('detailFailed').textContent = run.failed_samples;
            
            var stats = run.statistics || {{}};
            var fmt = function(v) {{ return (v !== null && v !== undefined) ? Number(v).toFixed(6) : 'N/A'; }};
            document.getElementById('detailMean').textContent = fmt(stats.mean);
            document.getElementById('detailMedian').textContent = fmt(stats.median);
            document.getElementById('detailMin').textContent = fmt(stats.min);
            document.getElementById('detailMax').textContent = fmt(stats.max);
            document.getElementById('detailStdDev').textContent = fmt(stats.std_dev);
            
            destroyCharts(currentDetailCharts);
            
            var validVals = [];
            var timeSeriesLabels = [];
            var timeSeriesData = [];
            var statusTimelineData = [];
            var statusColors = [];
            
            if (run.measurements && run.measurements.length > 0) {{
                run.measurements.forEach(function(m, idx) {{
                    if (m.success && m.value !== null) {{
                        validVals.push(m.value);
                        timeSeriesLabels.push(idx + 1);
                        timeSeriesData.push(m.value);
                        statusTimelineData.push(1);
                        statusColors.push('#28a745');
                    }} else {{
                        statusTimelineData.push(0);
                        statusColors.push('#dc3545');
                    }}
                }});
                
                var ctxTime = document.getElementById('chartTimeSeries').getContext('2d');
                var gradTime = ctxTime.createLinearGradient(0, 0, 0, 250);
                gradTime.addColorStop(0, 'rgba(59, 130, 246, 0.25)');
                gradTime.addColorStop(1, 'rgba(59, 130, 246, 0.0)');
                currentDetailCharts.push(new Chart(ctxTime, {{
                    type: 'line',
                    data: {{ labels: timeSeriesLabels, datasets: [{{ label: 'Current (A)', data: timeSeriesData, borderColor: '#3b82f6', backgroundColor: gradTime, fill: true, tension: 0.3, borderWidth: 2.5, pointRadius: 4, pointHoverRadius: 7 }}] }},
                    options: {{ responsive: true, maintainAspectRatio: false, plugins: {{ title: {{ display: true, text: 'Current Over Time' }} }}, scales: {{ y: {{ grid: {{ color: '#f3f4f6' }} }}, x: {{ grid: {{ display: false }} }} }} }}
                }}));
                
                var histChart = drawHistogram('chartHistogram', validVals);
                if (histChart) currentDetailCharts.push(histChart);
                
                var allLabels = Array.from({{length: run.measurements.length}}, (_, i) => i + 1);
                var ctxStatus = document.getElementById('chartStatusTimeline').getContext('2d');
                currentDetailCharts.push(new Chart(ctxStatus, {{
                    type: 'bar',
                    data: {{ labels: allLabels, datasets: [{{ label: 'Status (1=Pass, 0=Fail)', data: statusTimelineData, backgroundColor: statusColors, borderRadius: 3 }}] }},
                    options: {{ 
                        responsive: true, maintainAspectRatio: false, 
                        plugins: {{ title: {{ display: true, text: 'Sample Status Timeline' }}, tooltip: {{ callbacks: {{ label: function(c) {{ var m = run.measurements[c.dataIndex]; return m.success ? 'PASS: ' + m.value + 'A' : 'FAIL: ' + (m.error_type || 'Error'); }} }} }} }},
                        scales: {{ y: {{ min: 0, max: 1.2, ticks: {{ stepSize: 1, callback: function(v) {{ return v===1 ? 'PASS' : (v===0 ? 'FAIL' : ''); }} }} }} }}
                    }}
                }}));
            }}
            
            var errorsDiv = document.getElementById('detailErrors');
            var errors = run.errors || [];
            if (errors.length > 0) {{
                var html = '<h3>Errors</h3><ul>';
                for (var i = 0; i < errors.length; i++) {{
                    html += '<li><strong>' + (errors[i].error_type || 'Unknown') + '</strong>: ' + (errors[i].error_message || '') + '</li>';
                }}
                html += '</ul>';
                errorsDiv.innerHTML = html;
                errorsDiv.style.display = 'block';
            }} else {{ 
                errorsDiv.style.display = 'none'; 
            }}
            
            document.getElementById('detailOverlay').style.display = 'block';
            document.getElementById('detailPanel').style.display = 'block';
        }}
        
        function closeDetail() {{
            document.getElementById('detailPanel').style.display = 'none';
            document.getElementById('detailOverlay').style.display = 'none';
        }}
        
        function sortTable(n, tableId) {{
            var table, rows, switching, i, x, y, shouldSwitch, dir, switchcount = 0;
            table = document.getElementById(tableId);
            switching = true; dir = "asc";
            while (switching) {{
                switching = false;
                rows = table.getElementsByTagName("TR");
                for (i = 1; i < (rows.length - 1); i++) {{
                    shouldSwitch = false;
                    var tdX = rows[i].getElementsByTagName("TD");
                    var tdY = rows[i + 1].getElementsByTagName("TD");
                    if (tdX.length <= n || tdY.length <= n) continue;
                    x = tdX[n]; y = tdY[n];
                    var xVal = x.getAttribute("data-sort") || x.innerText;
                    var yVal = y.getAttribute("data-sort") || y.innerText;
                    var xNum = parseFloat(xVal); var yNum = parseFloat(yVal);
                    if (!isNaN(xNum) && !isNaN(yNum)) {{ xVal = xNum; yVal = yNum; }}
                    else {{ xVal = xVal.toLowerCase(); yVal = yVal.toLowerCase(); }}
                    if (dir == "asc") {{ if (xVal > yVal) {{ shouldSwitch = true; break; }} }}
                    else if (dir == "desc") {{ if (xVal < yVal) {{ shouldSwitch = true; break; }} }}
                }}
                if (shouldSwitch) {{ rows[i].parentNode.insertBefore(rows[i + 1], rows[i]); switching = true; switchcount++; }}
                else {{ if (switchcount == 0 && dir == "asc") {{ dir = "desc"; switching = true; }} }}
            }}
            var headers = table.rows[0].getElementsByTagName("TH");
            for (var j = 0; j < headers.length; j++) {{ var icon = headers[j].querySelector(".sort-icon"); if (icon) icon.innerHTML = "&#8597;"; }}
            var activeIcon = headers[n].querySelector(".sort-icon");
            if (activeIcon) {{ activeIcon.innerHTML = (dir === "asc") ? "&#8593;" : "&#8595;"; activeIcon.style.color = "#3b82f6"; }}
        }}
        
        window.onload = function() {{
            initGlobalCharts();
        }};
    </script>
</head>
<body>

    <!-- Navbar -->
    <div class="navbar">
        <div class="navbar-brand">Test QA Framework</div>
        <button id="btn-home" class="nav-btn active" onclick="switchTab('home')">Home</button>
        <button id="btn-analytics" class="nav-btn" onclick="switchTab('analytics')">Full Dashboard</button>
    </div>

    <!-- Modal for Detailed Run Report -->
    <div class="detail-overlay" id="detailOverlay" onclick="closeDetail()"></div>
    <div class="detail-panel" id="detailPanel">
        <div class="detail-header">
            <div>
                <h2 id="detailTitle" style="margin:0"></h2>
                <p style="color:#6c757d;margin:5px 0"><strong>Test ID:</strong> <span id="detailTestId"></span></p>
                <p style="color:#6c757d;margin:5px 0"><strong>Timestamp:</strong> <span id="detailTimestamp"></span></p>
            </div>
            <div style="display:flex;align-items:center;gap:15px">
                <span id="detailStatus" class="status-badge"></span>
                <button class="detail-close" onclick="closeDetail()">&times;</button>
            </div>
        </div>
        
        <h3>Execution Summary</h3>
        <table>
            <tr><th>Mode</th><th>Frequency (Hz)</th><th>Expected</th><th>Attempted</th><th>Successful</th><th>Failed</th></tr>
            <tr><td id="detailMode"></td><td id="detailFrequency"></td><td id="detailExpected"></td><td id="detailAttempted"></td><td id="detailSuccessful"></td><td id="detailFailed"></td></tr>
        </table>
        
        <h3>Statistical Data</h3>
        <table>
            <tr><th>Mean (A)</th><th>Median (A)</th><th>Min (A)</th><th>Max (A)</th><th>Std Dev (A)</th></tr>
            <tr><td id="detailMean"></td><td id="detailMedian"></td><td id="detailMin"></td><td id="detailMax"></td><td id="detailStdDev"></td></tr>
        </table>
        
        <div class="grid-2">
            <div class="graph-card"><canvas id="chartTimeSeries"></canvas></div>
            <div class="graph-card"><canvas id="chartHistogram"></canvas></div>
        </div>
        <div class="graph-card full-width-graph">
            <canvas id="chartStatusTimeline"></canvas>
        </div>
        
        <div class="detail-errors" id="detailErrors"></div>
    </div>

    <!-- TAB: HOME -->
    <div id="tab-home" class="tab-content active">
        <div class="container">
            <h2 style="margin-top:0">Global Statistics Overview</h2>
            <div class="grid-2">
                <div class="graph-card home-graph"><canvas id="globalPieChart"></canvas></div>
                <div class="graph-card home-graph"><canvas id="globalBarChart"></canvas></div>
            </div>
        </div>
        
        <div class="container">
            <h2 style="margin-top:0">Relative Consistency Analysis</h2>
            <table id="consistencyTable">
                <thead><tr>
                    <th onclick="sortTable(0, 'consistencyTable')">Ammeter Type <span class="sort-icon">&#8597;</span></th>
                    <th onclick="sortTable(1, 'consistencyTable')">Historical Runs <span class="sort-icon">&#8597;</span></th>
                    <th onclick="sortTable(2, 'consistencyTable')">Mean of Means (A) <span class="sort-icon">&#8597;</span></th>
                    <th onclick="sortTable(3, 'consistencyTable')">Std Dev of Means (A) <span class="sort-icon">&#8597;</span></th>
                </tr></thead>
                <tbody>{consistency_html}</tbody>
            </table>
        </div>
        
        <div class="container">
            <h2 style="margin-top:0">Recent Execution History</h2>
            <table id="runsTable">
                <thead><tr>
                    <th onclick="sortTable(0, 'runsTable')">Timestamp <span class="sort-icon">&#8597;</span></th>
                    <th onclick="sortTable(1, 'runsTable')">Ammeter Type <span class="sort-icon">&#8597;</span></th>
                    <th onclick="sortTable(2, 'runsTable')">Expected Samples <span class="sort-icon">&#8597;</span></th>
                    <th onclick="sortTable(3, 'runsTable')">Successful Samples <span class="sort-icon">&#8597;</span></th>
                    <th onclick="sortTable(4, 'runsTable')">Pass Rate <span class="sort-icon">&#8597;</span></th>
                    <th onclick="sortTable(5, 'runsTable')">Status <span class="sort-icon">&#8597;</span></th>
                    <th>Action</th>
                </tr></thead>
                <tbody>{runs_html}</tbody>
            </table>
        </div>
    </div>

    <!-- TAB: FULL DASHBOARD (ANALYTICS) -->
    <div id="tab-analytics" class="tab-content">
        
        {accuracy_assessment_html}

        <div class="container" style="background:transparent; border:none; box-shadow:none; padding:0">
            <div class="grid-2">
                <div class="graph-card"><canvas id="chartPassRateTrend"></canvas></div>
                <div class="graph-card"><canvas id="chartMeanStability"></canvas></div>
                <div class="graph-card"><canvas id="chartErrorDist"></canvas></div>
                <div class="graph-card"><canvas id="chartVolume"></canvas></div>
            </div>
        </div>
    </div>

</body>
</html>
"""
