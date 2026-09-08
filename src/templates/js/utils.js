const getChartOptions = (titleText) => ({
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    title: { display: !!titleText, text: titleText || "" },
  },
  scales: {
    y: { beginAtZero: true, grid: { color: "#f3f4f6" } },
    x: { grid: { display: false } },
  },
});

const destroyCharts = (chartArray) => {
  chartArray.forEach((c) => c.destroy());
  chartArray.length = 0;
};

const drawHistogram = (canvasId, values) => {
  if (values.length === 0) return null;
  const min = Math.min(...values);
  const max = Math.max(...values);
  const bins = 10;
  const binSize = (max - min) / bins || 1;

  const counts = new Array(bins).fill(0);
  values.forEach((v) => {
    let idx = Math.floor((v - min) / binSize);
    if (idx >= bins) idx = bins - 1;
    counts[idx]++;
  });

  const labels = [];
  for (let i = 0; i < bins; i++) {
    const b1 = min + i * binSize;
    const b2 = min + (i + 1) * binSize;
    labels.push(`${b1.toFixed(3)} - ${b2.toFixed(3)}`);
  }

  const ctx = document.getElementById(canvasId).getContext("2d");
  
  const options = getChartOptions("Value Distribution");
  options.scales.x.ticks = { display: false };

  return new Chart(ctx, {
    type: "bar",
    data: {
      labels: labels,
      datasets: [
        {
          label: "Frequency",
          data: counts,
          backgroundColor: "rgba(139, 92, 246, 0.6)",
          borderColor: "#8b5cf6",
          borderWidth: 1,
          borderRadius: 4,
        },
      ],
    },
    options: options,
  });
};
