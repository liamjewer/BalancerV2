// iframe and its parent panel
const frame = document.getElementById('controller');
const panel = document.getElementById('drive');

// native GamePad Viewer size
const NATIVE_W = 480*0.6;
const NATIVE_H = 300*0.6;

function scaleFrame() {
  const cs = getComputedStyle(panel);

  // panel padding
  const padX = parseFloat(cs.paddingLeft) + parseFloat(cs.paddingRight);
  const padY = parseFloat(cs.paddingTop) + parseFloat(cs.paddingBottom);

  // offset for heading height
  const title = panel.querySelector('h2');
  const titleH = title ? title.offsetHeight + parseFloat(cs.rowGap || 0) : 0;
  const availW = panel.clientWidth - padX;
  const availH = panel.clientHeight - padY - titleH;

  // calculate scale factor
  const scale = Math.min(availW / NATIVE_W, availH / NATIVE_H);

  panel.style.position = 'relative';

  // render iframe at native size, then CSS scales it down/up
  Object.assign(frame.style, {
    position: 'absolute',
    left: cs.paddingLeft, // line up with panel padding
    top: (parseFloat(cs.paddingTop) + titleH) + 'px', // offset for heading
    width: NATIVE_W + 'px',
    height: NATIVE_H + 'px',
    border: '0',
    transformOrigin: 'top left',
    transform: `scale(${scale})`
  });
}

// inturrupt for resize events 
new ResizeObserver(scaleFrame).observe(panel);

// init run
scaleFrame();