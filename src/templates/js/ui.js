function switchTab(tabId) {
  document.querySelectorAll(".tab-content").forEach(function (el) {
    el.classList.remove("active");
  });
  document.querySelectorAll(".nav-btn").forEach(function (el) {
    el.classList.remove("active");
  });

  document.getElementById("tab-" + tabId).classList.add("active");
  document.getElementById("btn-" + tabId).classList.add("active");

  if (tabId === "analytics" && analyticsCharts.length === 0) {
    initAnalyticsCharts();
  }
}

function showDetail(index) {
  var run = ALL_RUNS[index];
  if (!run) return;
  document.getElementById("detailTitle").textContent =
    run.ammeter_type.toUpperCase() + " Report";
  document.getElementById("detailTestId").textContent = run.test_id;
  document.getElementById("detailTimestamp").textContent = run.formatted_time;
  var statusEl = document.getElementById("detailStatus");
  statusEl.textContent = run.status;
  statusEl.className = "status-badge " + run.status.toLowerCase();
  document.getElementById("detailMode").textContent = run.configuration
    ? run.configuration.mode.toUpperCase()
    : "N/A";
  document.getElementById("detailFrequency").textContent = run.configuration
    ? run.configuration.sampling_frequency_hz
    : "N/A";
  document.getElementById("detailExpected").textContent = run.expected_samples;
  document.getElementById("detailAttempted").textContent =
    run.attempted_samples;
  document.getElementById("detailSuccessful").textContent =
    run.successful_samples;
  document.getElementById("detailFailed").textContent = run.failed_samples;

  var stats = run.statistics || {};
  var fmt = function (v) {
    return v !== null && v !== undefined ? Number(v).toFixed(6) : "N/A";
  };
  document.getElementById("detailMean").textContent = fmt(stats.mean);
  document.getElementById("detailMedian").textContent = fmt(stats.median);
  document.getElementById("detailMin").textContent = fmt(stats.min);
  document.getElementById("detailMax").textContent = fmt(stats.max);
  document.getElementById("detailStdDev").textContent = fmt(stats.std_dev);

  destroyCharts(currentDetailCharts);

  var validVals = [];
  var timeSeriesLabels = [];
  var timeSeriesData = [];
  var statusTimelineData = [];
  var statusColors = [];

  if (run.measurements && run.measurements.length > 0) {
    run.measurements.forEach(function (m, idx) {
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

    var ctxTime = document.getElementById("chartTimeSeries").getContext("2d");
    var gradTime = ctxTime.createLinearGradient(0, 0, 0, 250);
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
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { title: { display: true, text: "Current Over Time" } },
          scales: {
            y: { grid: { color: "#f3f4f6" } },
            x: { grid: { display: false } },
          },
        },
      }),
    );

    var histChart = drawHistogram("chartHistogram", validVals);
    if (histChart) currentDetailCharts.push(histChart);

    var allLabels = Array.from(
      { length: run.measurements.length },
      (_, i) => i + 1,
    );
    var ctxStatus = document
      .getElementById("chartStatusTimeline")
      .getContext("2d");
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
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            title: { display: true, text: "Sample Status Timeline" },
            tooltip: {
              callbacks: {
                label: function (c) {
                  var m = run.measurements[c.dataIndex];
                  return m.success
                    ? "PASS: " + m.value + "A"
                    : "FAIL: " + (m.error_type || "Error");
                },
              },
            },
          },
          scales: {
            y: {
              min: 0,
              max: 1.2,
              ticks: {
                stepSize: 1,
                callback: function (v) {
                  return v === 1 ? "PASS" : v === 0 ? "FAIL" : "";
                },
              },
            },
          },
        },
      }),
    );
  }

  var errorsDiv = document.getElementById("detailErrors");
  var errors = run.errors || [];
  if (errors.length > 0) {
    var html = "<h3>Errors</h3><ul>";
    for (var i = 0; i < errors.length; i++) {
      html +=
        "<li><strong>" +
        (errors[i].error_type || "Unknown") +
        "</strong>: " +
        (errors[i].error_message || "") +
        "</li>";
    }
    html += "</ul>";
    errorsDiv.innerHTML = html;
    errorsDiv.style.display = "block";
  } else {
    errorsDiv.style.display = "none";
  }

  document.getElementById("detailOverlay").style.display = "block";
  document.getElementById("detailPanel").style.display = "block";
}

function closeDetail() {
  document.getElementById("detailPanel").style.display = "none";
  document.getElementById("detailOverlay").style.display = "none";
}

function sortTable(n, tableId) {
  var table,
    rows,
    switching,
    i,
    x,
    y,
    shouldSwitch,
    dir,
    switchcount = 0;
  table = document.getElementById(tableId);
  switching = true;
  dir = "asc";
  while (switching) {
    switching = false;
    rows = table.getElementsByTagName("TR");
    for (i = 1; i < rows.length - 1; i++) {
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
      if (!isNaN(xNum) && !isNaN(yNum)) {
        xVal = xNum;
        yVal = yNum;
      } else {
        xVal = xVal.toLowerCase();
        yVal = yVal.toLowerCase();
      }
      if (dir == "asc") {
        if (xVal > yVal) {
          shouldSwitch = true;
          break;
        }
      } else if (dir == "desc") {
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
      if (switchcount == 0 && dir == "asc") {
        dir = "desc";
        switching = true;
      }
    }
  }
  var headers = table.rows[0].getElementsByTagName("TH");
  for (var j = 0; j < headers.length; j++) {
    var icon = headers[j].querySelector(".sort-icon");
    if (icon) icon.innerHTML = "&#8597;";
  }
  var activeIcon = headers[n].querySelector(".sort-icon");
  if (activeIcon) {
    activeIcon.innerHTML = dir === "asc" ? "&#8593;" : "&#8595;";
    activeIcon.style.color = "#3b82f6";
  }
}
