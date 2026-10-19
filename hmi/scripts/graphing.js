const ctx = document.getElementById('dataChart');

  new Chart(ctx, {
    type: 'line',
    data: {
      labels: [1, 5, 10, 15, 20, 25],
      datasets: [{
        label:'lMotorSpeed',
        data: [12, 19, 3, 5, 2, 3],
        borderWidth: 1,
        stepped: true
      }]
    },
    options: {
      scales: {
        y: {
          beginAtZero: true
        }
      },
      maintainAspectRatio: false
    }
  });