//TODO: update values from file

document.querySelector('.tuning-table').addEventListener('click', (e) => {
  const btn = e.target.closest('.row-sync');
  if (!btn) return;

  const input = btn.closest('tr').querySelector('input');
  console.log("transmitting tuning values...")
  send("tuning", { [btn.dataset.constant]: Number(input.value) });

  btn.querySelector('svg').classList.toggle('spin');
});