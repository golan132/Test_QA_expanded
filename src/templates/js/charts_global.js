const initGlobalCharts = () => {
  if (!ALL_RUNS || ALL_RUNS.length === 0) return;

  const statusCounts = { PASS: 0, FAIL: 0, ERROR: 0, PARTIAL: 0 };
  const ammeterTypes = {};

  ALL_RUNS.forEach((run) => {
    const s = run.status.toUpperCase();
    if (statusCounts[s] !== undefined) statusCounts[s]++;
    else statusCounts[s] = 1;

    const am = run.ammeter_type;
    if (!ammeterTypes[am]) ammeterTypes[am] = { pass: 0, total: 0 };
    ammeterTypes[am].total++;
    if (s === "PASS") ammeterTypes[am].pass++;
  });

  const pieColors = {
    PASS: "#28a745",
    FAIL: "#dc3545",
    ERROR: "#ffc107",
    PARTIAL: "#0dcaf0",
  };
  
  const pieLabels = Object.keys(statusCounts).filter((k) => statusCounts[k] > 0);
  const pieData = pieLabels.map((k) => statusCounts[k]);
  const pieBgColors = pieLabels.map((k) => pieColors[k] || "#6c757d");

  const ctxPie = document.getElementById("globalPieChart").getContext("2d");
  
  const pieOptions = getChartOptions("Overall Run Status Distribution");
  pieOptions.cutout = "60%";
  delete pieOptions.scales; // Pie charts don't have scales

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
      options: pieOptions,
    })
  );

  const amLabels = Object.keys(ammeterTypes);
  const amData = amLabels.map(
    (k) => (ammeterTypes[k].pass / ammeterTypes[k].total) * 100
  );

  const ctxBar = document.getElementById("globalBarChart").getContext("2d");
  
  const barOptions = getChartOptions("Pass Rate by Ammeter Type (%)");
  barOptions.plugins.legend = { display: false };
  barOptions.scales.y.max = 100;

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
      options: barOptions,
    })
  );
};
