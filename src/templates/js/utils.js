function destroyCharts(chartArray) {
  chartArray.forEach(function (c) {
    c.destroy();
  });
  chartArray.length = 0;
}

function drawHistogram(canvasId, values) {
  if (values.length === 0) return null;
  var min = Math.min(...values);
  var max = Math.max(...values);
  var bins = 10;
  var binSize = (max - min) / bins || 1;

  var counts = new Array(bins).fill(0);
  values.forEach(function (v) {
    var idx = Math.floor((v - min) / binSize);
    if (idx >= bins) idx = bins - 1;
    counts[idx]++;
  });

  var labels = [];
  for (var i = 0; i < bins; i++) {
    var b1 = min + i * binSize;
    var b2 = min + (i + 1) * binSize;
    labels.push(b1.toFixed(3) + " - " + b2.toFixed(3));
  }

  var ctx = document.getElementById(canvasId).getContext("2d");
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
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { title: { display: true, text: "Value Distribution" } },
      scales: {
        y: { beginAtZero: true, grid: { color: "#f3f4f6" } },
        x: { grid: { display: false }, ticks: { display: false } },
      },
    },
  });
}
