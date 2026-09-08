function initAnalyticsCharts() {
  if (!ALL_RUNS || ALL_RUNS.length === 0) return;

  // Reverse so oldest is first
  var chronologicalRuns = [...ALL_RUNS].reverse();

  var timeLabels = [];
  var passRateData = [];

  var ammeterMeans = {};
  var errorTypes = {};
  var volumeByDate = {};

  chronologicalRuns.forEach(function (run) {
    var label = run.formatted_time;
    timeLabels.push(label);

    // Pass Rate
    var pr =
      run.expected_samples > 0
        ? (run.successful_samples / run.expected_samples) * 100
        : 0;
    passRateData.push(pr);

    // Mean Stability
    var am = run.ammeter_type;
    if (!ammeterMeans[am]) ammeterMeans[am] = [];
    // Pad previous missing points with null
    while (ammeterMeans[am].length < timeLabels.length - 1)
      ammeterMeans[am].push(null);
    ammeterMeans[am].push(run.statistics ? run.statistics.mean : null);

    // Volume
    var d = label.split(" ")[0];
    if (!volumeByDate[d]) volumeByDate[d] = 0;
    volumeByDate[d] += run.attempted_samples;

    // Errors
    if (run.errors) {
      run.errors.forEach(function (e) {
        var t = e.error_type || "Unknown";
        if (!errorTypes[t]) errorTypes[t] = 0;
        errorTypes[t]++;
      });
    }
  });

  // Pad all ammeter means to the end
  Object.keys(ammeterMeans).forEach((k) => {
    while (ammeterMeans[k].length < timeLabels.length)
      ammeterMeans[k].push(null);
  });

  // 1. Pass Rate Trend
  var ctxPass = document.getElementById("chartPassRateTrend").getContext("2d");
  var gradPass = ctxPass.createLinearGradient(0, 0, 0, 300);
  gradPass.addColorStop(0, "rgba(16, 185, 129, 0.3)");
  gradPass.addColorStop(1, "rgba(16, 185, 129, 0.0)");
  analyticsCharts.push(
    new Chart(ctxPass, {
      type: "line",
      data: {
        labels: timeLabels,
        datasets: [
          {
            label: "Pass Rate (%)",
            data: passRateData,
            borderColor: "#10b981",
            backgroundColor: gradPass,
            fill: true,
            tension: 0.4,
            borderWidth: 2.5,
            pointRadius: 3,
            pointHoverRadius: 6,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          title: { display: true, text: "System Stability (Pass Rate Trend)" },
        },
        scales: {
          y: { min: 0, max: 100, grid: { color: "#f3f4f6" } },
          x: { grid: { display: false }, ticks: { maxTicksLimit: 8 } },
        },
      },
    }),
  );

  // 2. Mean Stability
  var meanDatasets = [];
  var colors = ["#3b82f6", "#ef4444", "#f59e0b", "#8b5cf6", "#14b8a6"];
  Object.keys(ammeterMeans).forEach((k, i) => {
    meanDatasets.push({
      label: k.toUpperCase(),
      data: ammeterMeans[k],
      borderColor: colors[i % colors.length],
      spanGaps: true,
      tension: 0.35,
      borderWidth: 2.5,
      pointRadius: 3,
      pointHoverRadius: 6,
    });
  });
  var ctxMean = document.getElementById("chartMeanStability").getContext("2d");
  analyticsCharts.push(
    new Chart(ctxMean, {
      type: "line",
      data: { labels: timeLabels, datasets: meanDatasets },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          title: { display: true, text: "Mean Current (A) Stability" },
        },
        scales: {
          y: { grid: { color: "#f3f4f6" } },
          x: { grid: { display: false }, ticks: { maxTicksLimit: 8 } },
        },
      },
    }),
  );

  // 3. Error Distribution
  var errLabels = Object.keys(errorTypes);
  var errData = errLabels.map((k) => errorTypes[k]);
  var ctxErr = document.getElementById("chartErrorDist").getContext("2d");
  if (errLabels.length > 0) {
    analyticsCharts.push(
      new Chart(ctxErr, {
        type: "doughnut",
        data: {
          labels: errLabels,
          datasets: [
            {
              data: errData,
              backgroundColor: colors,
              borderWidth: 0,
              hoverOffset: 6,
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          cutout: "55%",
          plugins: {
            title: { display: true, text: "Error Type Distribution" },
          },
        },
      }),
    );
  } else {
    // No errors
    var noErrCtx = ctxErr;
    noErrCtx.font = "14px Arial";
    noErrCtx.textAlign = "center";
    noErrCtx.fillText(
      "No Errors Recorded",
      ctxErr.canvas.width / 2,
      ctxErr.canvas.height / 2,
    );
  }

  // 4. Execution Volume
  var volLabels = Object.keys(volumeByDate);
  var volData = volLabels.map((k) => volumeByDate[k]);
  var ctxVol = document.getElementById("chartVolume").getContext("2d");
  analyticsCharts.push(
    new Chart(ctxVol, {
      type: "bar",
      data: {
        labels: volLabels,
        datasets: [
          {
            label: "Attempted Samples",
            data: volData,
            backgroundColor: "#06b6d4",
            borderRadius: 6,
            barPercentage: 0.5,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { title: { display: true, text: "Testing Volume by Date" } },
        scales: {
          y: { beginAtZero: true, grid: { color: "#f3f4f6" } },
          x: { grid: { display: false } },
        },
      },
    }),
  );
}
