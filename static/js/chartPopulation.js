const ctx = document.getElementById("insect-population-chart");

new Chart(ctx, {
  type: "bar",
  data: {
    labels: [
      "Jan",
      "Feb",
      "Mar",
      "Apr",
      "May",
      "Jun",
      "Jul",
      "Aug",
      "Sep",
      "Oct",
      "Nov",
      "Dec",
    ],
    datasets: [
      {
        label: "Recorded",
        data: [12, 19, 3, 5, 2, 3, null, null, null, null, null, null],
        backgroundColor: ["#007837"],
        borderWidth: 0,
      },
      {
        label: "Predicted",
        data: [null, null, null, null, null, null, 3, 3, 3, 4, 5, 6],
        backgroundColor: ["#c4820a"],
        borderWidth: 0,
      },
    ],
  },
  options: {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: "bottom",
      },
    },
    scales: {
      y: {
        display: false,
        beginAtZero: true,
      },
      x: {
        grid: {
          display: false,
        },
      },
      y: {
        grid: {
          display: false,
        },
      },
    },
  },
});
