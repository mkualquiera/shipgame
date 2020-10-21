
var hostname = document.location.hostname;
var huesync = new HueSync("ws://" + hostname + ":60606/");
huesync.ws.onopen = function () {
    var rackelem = document.getElementById("rack");
    var rackmanager = new RackManager(rackelem,
        huesync,
        "ship");
    var kines = rackmanager.addElement(KinematicsElement, 
        "kinematics");
    var fthrottle = rackmanager.addElement(SliderElement, 
        "forward_throttle");
    fthrottle.slider.min = -5;
    fthrottle.slider.max = 5;
    var rthrottle = rackmanager.addElement(SliderElement, 
        "right_throttle");
    rthrottle.slider.min = -5;
    rthrottle.slider.max = 5;
    var athrottle = rackmanager.addElement(SliderElement, 
        "angular_throttle");
    athrottle.slider.min = -5;
    athrottle.slider.max = 5;
}

