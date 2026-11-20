let selected = [];
let paused = false;

const chart = new Chart(document.getElementById('dataChart'), {
  type: 'line',
  data: { datasets: [] },
  options: {
    animation: false,
    parsing: false,
    scales: { x: { type: 'linear' }, y: { beginAtZero: true } },
    maintainAspectRatio: false
  }
});

function updateGraph() {
  chart.data.datasets = selected.map(name => ({
    label: name,
    data: samples.map(s => ({ x: s.t, y: s[name] })),
    borderWidth: 1,
    pointRadius: 0,
    stepped: true
  }));
  chart.update('none');
}

document.getElementById('selections').addEventListener('change', refreshSelection);
refreshSelection();

function refreshSelection() {
  selected = [...document.querySelectorAll('#selections input:checked')]
    .map(box => box.value);
  samples.length = 0;
}

pauseButton = document.getElementById('pause');
pauseButton.addEventListener('click', pauseGraph);

function pauseGraph() {
  if(paused){
    pauseButton.innerHTML = '<i data-lucide="pause"></i>';
    paused = false;
  }else{
    pauseButton.innerHTML = '<i data-lucide="play"></i>';
    paused = true;
  }

  lucide.createIcons();
}