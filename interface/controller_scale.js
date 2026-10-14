function controller_scale() {
    const controller = document.getElementById("controller");
    controller.src = "https://app.gpv.gg/?p=1&s=0&sc=" + ((0.2/250)*controller.clientWidth);
    console.log(controller.clientWidth);
}

// event listener
new ResizeObserver(controller_scale).observe(document.getElementById("controller"));

// init run
controller_scale();