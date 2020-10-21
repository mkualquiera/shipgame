
var hostname = document.location.hostname;
var huesync = new HueSync("ws://" + hostname + ":60606/");
huesync.ws.onopen = function () {
    var rackelem = document.getElementById("rack");
    var rackmanager = new RackManager(rackelem,
        huesync,
        "ship");
    var sheading = rackmanager.addElement(DialElement, "desired_heading");
    sheading.max = 360;
    sheading.sensitivity = 240;
    var sthrottle = rackmanager.addElement(SliderElement, "throttle");
}

