//load tuning from config file
fetch('/config/tuning.json', { cache: 'no-store' })
  .then((res) => res.json())
  .then((data) => {
    for (const [key, value] of Object.entries(data)) {
      const btn = document.querySelector(`.tuning-table .row-sync[data-constant="${key}"]`);
      if (btn && value != null) {
        btn.closest('tr').querySelector('input').value = value;
      }
    }
  })
  .catch((err) => console.error('Failed to load tuning.json:', err));

document.querySelector('.tuning-table').addEventListener('click', (e) => {
  const btn = e.target.closest('.row-sync');
  if (!btn) return;

  const input = btn.closest('tr').querySelector('input');
  console.log("transmitting tuning values...")
  send("tuning", { [btn.dataset.constant]: Number(input.value) });

  btn.querySelector('svg').classList.toggle('spin');
});