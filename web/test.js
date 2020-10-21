
var hostname = document.location.hostname;
var huesync = new HueSync("ws://" + hostname + ":60606/");
huesync.ws.onopen = function () {
    var rackelem = document.getElementById("rack");
    var rackmanager = new RackManager(rackelem,
        huesync,
        "ship");
    var fthrottle = rackmanager.addElement(SliderElement, 
        "forward_throttle");
    fthrottle.slider.min = -100;
    fthrottle.slider.max = 100;
    var rthrottle = rackmanager.addElement(SliderElement, 
        "right_throttle");
    rthrottle.slider.min = -100;
    rthrottle.slider.max = 100;
    var athrottle = rackmanager.addElement(SliderElement, 
        "angular_throttle");
    athrottle.slider.min = -100;
    athrottle.slider.max = 100;
}

