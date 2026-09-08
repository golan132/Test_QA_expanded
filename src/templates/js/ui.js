const switchTab = (tabId) => {
  document.querySelectorAll(".tab-content").forEach((el) => {
    el.classList.remove("active");
  });
  document.querySelectorAll(".nav-btn").forEach((el) => {
    el.classList.remove("active");
  });

  document.getElementById(`tab-${tabId}`).classList.add("active");
  document.getElementById(`btn-${tabId}`).classList.add("active");

  if (tabId === "analytics" && analyticsCharts.length === 0) {
    initAnalyticsCharts();
  }
};

const showDetail = (index) => {
  const run = ALL_RUNS[index];
  if (!run) return;
  
  document.getElementById("detailTitle").textContent = `${run.ammeter_type.toUpperCase()} Report`;
  document.getElementById("detailTestId").textContent = run.test_id;
  document.getElementById("detailTimestamp").textContent = run.formatted_time;
  
  const statusEl = document.getElementById("detailStatus");
  statusEl.textContent = run.status;
  statusEl.className = `status-badge ${run.status.toLowerCase()}`;
  
  document.getElementById("detailMode").textContent = run.configuration
    ? run.configuration.mode.toUpperCase()
    : "N/A";
  document.getElementById("detailFrequency").textContent = run.configuration
    ? run.configuration.sampling_frequency_hz
    : "N/A";
  document.getElementById("detailExpected").textContent = run.expected_samples;
  document.getElementById("detailAttempted").textContent = run.attempted_samples;
  document.getElementById("detailSuccessful").textContent = run.successful_samples;
  document.getElementById("detailFailed").textContent = run.failed_samples;

  const stats = run.statistics || {};
  const fmt = (v) => (v !== null && v !== undefined ? Number(v).toFixed(6) : "N/A");
  
  document.getElementById("detailMean").textContent = fmt(stats.mean);
  document.getElementById("detailMedian").textContent = fmt(stats.median);
  document.getElementById("detailMin").textContent = fmt(stats.min);
  document.getElementById("detailMax").textContent = fmt(stats.max);
  document.getElementById("detailStdDev").textContent = fmt(stats.std_dev);

  destroyCharts(currentDetailCharts);

  const validVals = [];
  const timeSeriesLabels = [];
  const timeSeriesData = [];
  const statusTimelineData = [];
  const statusColors = [];

  if (run.measurements && run.measurements.length > 0) {
    run.measurements.forEach((m, idx) => {
      if (m.success && m.value !== null) {
        validVals.push(m.value);
        timeSeriesLabels.push(idx + 1);
        timeSeriesData.push(m.value);
        statusTimelineData.push(1);
        statusColors.push("#28a745");
      } else {
        statusTimelineData.push(0);
        statusColors.push("#dc3545");
      }
    });

    const ctxTime = document.getElementById("chartTimeSeries").getContext("2d");
    const gradTime = ctxTime.createLinearGradient(0, 0, 0, 250);
    gradTime.addColorStop(0, "rgba(59, 130, 246, 0.25)");
    gradTime.addColorStop(1, "rgba(59, 130, 246, 0.0)");
    
    currentDetailCharts.push(
      new Chart(ctxTime, {
        type: "line",
        data: {
          labels: timeSeriesLabels,
          datasets: [
            {
              label: "Current (A)",
              data: timeSeriesData,
              borderColor: "#3b82f6",
              backgroundColor: gradTime,
              fill: true,
              tension: 0.3,
              borderWidth: 2.5,
              pointRadius: 4,
              pointHoverRadius: 7,
            },
          ],
        },
        options: getChartOptions("Current Over Time"),
      })
    );

    const histChart = drawHistogram("chartHistogram", validVals);
    if (histChart) currentDetailCharts.push(histChart);

    const allLabels = Array.from({ length: run.measurements.length }, (_, i) => i + 1);
    const ctxStatus = document.getElementById("chartStatusTimeline").getContext("2d");
    
    const statusOptions = getChartOptions("Sample Status Timeline");
    statusOptions.plugins.tooltip = {
      callbacks: {
        label: (c) => {
          const m = run.measurements[c.dataIndex];
          return m.success ? `PASS: ${m.value}A` : `FAIL: ${m.error_type || "Error"}`;
        },
      },
    };
    statusOptions.scales.y.min = 0;
    statusOptions.scales.y.max = 1.2;
    statusOptions.scales.y.ticks = {
      stepSize: 1,
      callback: (v) => (v === 1 ? "PASS" : v === 0 ? "FAIL" : ""),
    };

    currentDetailCharts.push(
      new Chart(ctxStatus, {
        type: "bar",
        data: {
          labels: allLabels,
          datasets: [
            {
              label: "Status (1=Pass, 0=Fail)",
              data: statusTimelineData,
              backgroundColor: statusColors,
              borderRadius: 3,
            },
          ],
        },
        options: statusOptions,
      })
    );
  }

  const errorsDiv = document.getElementById("detailErrors");
  const errors = run.errors || [];
  if (errors.length > 0) {
    let html = "<h3>Errors</h3><ul>";
    for (let i = 0; i < errors.length; i++) {
      html += `<li><strong>${errors[i].error_type || "Unknown"}</strong>: ${errors[i].error_message || ""}</li>`;
    }
    html += "</ul>";
    errorsDiv.innerHTML = html;
    errorsDiv.style.display = "block";
  } else {
    errorsDiv.style.display = "none";
  }

  document.getElementById("detailOverlay").style.display = "block";
  document.getElementById("detailPanel").style.display = "block";
};

const closeDetail = () => {
  document.getElementById("detailPanel").style.display = "none";
  document.getElementById("detailOverlay").style.display = "none";
};

const sortTable = (n, tableId) => {
  const table = document.getElementById(tableId);
  let switching = true;
  let dir = "asc";
  let switchcount = 0;

  while (switching) {
    switching = false;
    const rows = table.getElementsByTagName("TR");
    let shouldSwitch = false;
    let i;
    for (i = 1; i < rows.length - 1; i++) {
      shouldSwitch = false;
      const tdX = rows[i].getElementsByTagName("TD");
      const tdY = rows[i + 1].getElementsByTagName("TD");
      if (tdX.length <= n || tdY.length <= n) continue;
      
      const x = tdX[n];
      const y = tdY[n];
      let xVal = x.getAttribute("data-sort") || x.innerText;
      let yVal = y.getAttribute("data-sort") || y.innerText;
      
      const xNum = parseFloat(xVal);
      const yNum = parseFloat(yVal);
      if (!isNaN(xNum) && !isNaN(yNum)) {
        xVal = xNum;
        yVal = yNum;
      } else {
        xVal = xVal.toLowerCase();
        yVal = yVal.toLowerCase();
      }
      
      if (dir === "asc") {
        if (xVal > yVal) {
          shouldSwitch = true;
          break;
        }
      } else if (dir === "desc") {
        if (xVal < yVal) {
          shouldSwitch = true;
          break;
        }
      }
    }
    if (shouldSwitch) {
      rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
      switching = true;
      switchcount++;
    } else {
      if (switchcount === 0 && dir === "asc") {
        dir = "desc";
        switching = true;
      }
    }
  }
  
  const headers = table.rows[0].getElementsByTagName("TH");
  for (let j = 0; j < headers.length; j++) {
    const icon = headers[j].querySelector(".sort-icon");
    if (icon) icon.innerHTML = "&#8597;";
  }
  
  const activeIcon = headers[n].querySelector(".sort-icon");
  if (activeIcon) {
    activeIcon.innerHTML = dir === "asc" ? "&#8593;" : "&#8595;";
    activeIcon.style.color = "#3b82f6";
  }
};
