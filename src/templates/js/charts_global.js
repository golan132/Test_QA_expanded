function initGlobalCharts() {
  if (!ALL_RUNS || ALL_RUNS.length === 0) return;

  var statusCounts = { PASS: 0, FAIL: 0, ERROR: 0, PARTIAL: 0 };
  var ammeterTypes = {};

  ALL_RUNS.forEach(function (run) {
    var s = run.status.toUpperCase();
    if (statusCounts[s] !== undefined) statusCounts[s]++;
    else statusCounts[s] = 1;

    var am = run.ammeter_type;
    if (!ammeterTypes[am]) ammeterTypes[am] = { pass: 0, total: 0 };
    ammeterTypes[am].total++;
    if (s === "PASS") ammeterTypes[am].pass++;
  });

  var pieColors = {
    PASS: "#28a745",
    FAIL: "#dc3545",
    ERROR: "#ffc107",
    PARTIAL: "#0dcaf0",
  };
  var pieLabels = Object.keys(statusCounts).filter((k) => statusCounts[k] > 0);
  var pieData = pieLabels.map((k) => statusCounts[k]);
  var pieBgColors = pieLabels.map((k) => pieColors[k] || "#6c757d");

  var ctxPie = document.getElementById("globalPieChart").getContext("2d");
  globalCharts.push(
    new Chart(ctxPie, {
      type: "doughnut",
      data: {
        labels: pieLabels,
        datasets: [
          {
            data: pieData,
            backgroundColor: pieBgColors,
            borderWidth: 0,
            hoverOffset: 6,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: "60%",
        plugins: {
          title: { display: true, text: "Overall Run Status Distribution" },
        },
      },
    }),
  );

  var amLabels = Object.keys(ammeterTypes);
  var amData = amLabels.map(
    (k) => (ammeterTypes[k].pass / ammeterTypes[k].total) * 100,
  );

  var ctxBar = document.getElementById("globalBarChart").getContext("2d");
  globalCharts.push(
    new Chart(ctxBar, {
      type: "bar",
      data: {
        labels: amLabels,
        datasets: [
          {
            label: "Pass Rate (%)",
            data: amData,
            backgroundColor: "#3b82f6",
            borderRadius: 6,
            barPercentage: 0.5,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          title: { display: true, text: "Pass Rate by Ammeter Type (%)" },
          legend: { display: false },
        },
        scales: {
          y: { min: 0, max: 100, grid: { color: "#f3f4f6" } },
          x: { grid: { display: false } },
        },
      },
    }),
  );
}
