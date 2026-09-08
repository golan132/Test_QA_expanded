const initAnalyticsCharts = () => {
  if (!ALL_RUNS || ALL_RUNS.length === 0) return;

  const chronologicalRuns = [...ALL_RUNS].reverse();

  const timeLabels = [];
  const passRateData = [];

  const ammeterMeans = {};
  const errorTypes = {};
  const volumeByDate = {};

  chronologicalRuns.forEach((run) => {
    const label = run.formatted_time;
    timeLabels.push(label);

    const pr = run.expected_samples > 0 ? (run.successful_samples / run.expected_samples) * 100 : 0;
    passRateData.push(pr);

    const am = run.ammeter_type;
    if (!ammeterMeans[am]) ammeterMeans[am] = [];
    while (ammeterMeans[am].length < timeLabels.length - 1) {
      ammeterMeans[am].push(null);
    }
    ammeterMeans[am].push(run.statistics ? run.statistics.mean : null);

    const d = label.split(" ")[0];
    if (!volumeByDate[d]) volumeByDate[d] = 0;
    volumeByDate[d] += run.attempted_samples;

    if (run.errors) {
      run.errors.forEach((e) => {
        const t = e.error_type || "Unknown";
        if (!errorTypes[t]) errorTypes[t] = 0;
        errorTypes[t]++;
      });
    }
  });

  Object.keys(ammeterMeans).forEach((k) => {
    while (ammeterMeans[k].length < timeLabels.length) ammeterMeans[k].push(null);
  });

  const ctxPass = document.getElementById("chartPassRateTrend").getContext("2d");
  const gradPass = ctxPass.createLinearGradient(0, 0, 0, 300);
  gradPass.addColorStop(0, "rgba(16, 185, 129, 0.3)");
  gradPass.addColorStop(1, "rgba(16, 185, 129, 0.0)");
  
  const passOptions = getChartOptions("System Stability (Pass Rate Trend)");
  passOptions.scales.y.max = 100;
  passOptions.scales.x.ticks = { maxTicksLimit: 8 };

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
      options: passOptions,
    })
  );

  const meanDatasets = [];
  const colors = ["#3b82f6", "#ef4444", "#f59e0b", "#8b5cf6", "#14b8a6"];
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
  
  const ctxMean = document.getElementById("chartMeanStability").getContext("2d");
  
  const meanOptions = getChartOptions("Mean Current (A) Stability");
  meanOptions.scales.x.ticks = { maxTicksLimit: 8 };

  analyticsCharts.push(
    new Chart(ctxMean, {
      type: "line",
      data: { labels: timeLabels, datasets: meanDatasets },
      options: meanOptions,
    })
  );

  const errLabels = Object.keys(errorTypes);
  const errData = errLabels.map((k) => errorTypes[k]);
  const ctxErr = document.getElementById("chartErrorDist").getContext("2d");
  if (errLabels.length > 0) {
    const errOptions = getChartOptions("Error Type Distribution");
    errOptions.cutout = "55%";
    delete errOptions.scales;

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
        options: errOptions,
      })
    );
  } else {
    ctxErr.font = "14px Arial";
    ctxErr.textAlign = "center";
    ctxErr.fillText("No Errors Recorded", ctxErr.canvas.width / 2, ctxErr.canvas.height / 2);
  }

  const volLabels = Object.keys(volumeByDate);
  const volData = volLabels.map((k) => volumeByDate[k]);
  const ctxVol = document.getElementById("chartVolume").getContext("2d");
  
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
      options: getChartOptions("Testing Volume by Date"),
    })
  );
};
