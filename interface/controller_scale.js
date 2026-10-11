function controller_scale() {
    const controller = document.getElementById("controller");
    controller.src = "https://app.gpv.gg/?p=1&s=0&sc=" + ((0.2/180)*controller.clientWidth);
}

// event listener
new ResizeObserver(scaleFrame).observe(panel);

// init run
scaleFrame();