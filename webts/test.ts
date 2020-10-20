

var hostname = document.location.hostname
var heading = document.getElementById('heading');
var huesync = new HueSync("ws://" + hostname + ":60606/");
var slider = document.getElementById('heading_s');

huesync.ws.onopen = function(ev) {
  huesync.subscribe("ship/desired_heading", function(ent) {
    console.debug(ent);
    slider.value = ent.value;
    heading.innerText = ent.value;
  });
}

slider.oninput = function () {
  huesync.database["ship/desired_heading"].setValue(slider.value);
}