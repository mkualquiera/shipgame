
var hostname = document.location.hostname;
var huesync = new HueSync("ws://" + hostname + ":60606/");
huesync.ws.onopen = function () {
    var rackelem = document.getElementById("rack");
    console.log(rackelem);
    var rackmanager = new RackManager(rackelem,
        huesync,
        "ship");
    var sheading = rackmanager.addElement(SliderElement, "desired_heading");
    sheading.slider.max = 360;
    var sthrottle = rackmanager.addElement(SliderElement, "throttle");
}