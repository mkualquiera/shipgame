document.body.isMouseDown = 0

document.body.onmousedown = function() {
    document.body.isMouseDown = 1;
}

document.body.ontouchstart = function() {
    document.body.isMouseDown = 1;
}

document.body.onmouseup = function() {
    document.body.isMouseDown = 0;
}

document.body.ontouchend = function() {
    document.body.isMouseDown = 0;
}

var RackManager = (function () {
    function RackManager(container, huesync, path) {
        this.path = path;
        this.huesync = huesync;
        this.container = container;
        this.elements = [];
    }
    RackManager.prototype.createElementContainer = function (name) {
        var newElem = document.createElement("div");
        newElem.innerHTML = "<div class='rackbound rackname'>"+ name 
            +"</div><div class='rackbound'></div>";
        this.container.appendChild(newElem);
        return newElem.children[1];
    }
    RackManager.prototype.addElement = function(ElemType, name) {
        var self = this;
        console.debug(self);
        var added = new ElemType(self.createElementContainer(name),
            self, name);
        this.elements.push(added);
        return added;
    };
    return RackManager;
}());

var RackElement = (function () {
    function RackElement(container, manager, name) {
        this.container = container;
        this.path = manager.path + "/" + name;
        this.manager = manager;
        this.value = {};
        this.onreceiveupdate = function() {};
        this.onuserinput = function () {
            var self = this;
            this.manager.huesync.database[self.path]
                    .setValue(self.value);    
        }
        var self = this;
        this.manager.huesync.subscribe(self.path, function (ent) {
            self.value = ent.value;
            self.onreceiveupdate(ent);
        });
    }
    return RackElement;
}());

var SliderElement = (function () {
    function SliderElement(container, manager, name) {
        RackElement.call(this, container, manager, name);
        var self = this;
        container.innerHTML = '<div></div><input type="range" min="0" max="100"'
        + 'value="50" class="slider">';
        this.text = container.children[0];
        this.slider = container.children[1];
        this.slider.oninput = function () {
            self.value = self.slider.value;
            self.onuserinput();
        };
        this.onreceiveupdate = function () {
            this.text.innerText = this.value;
            this.slider.value = this.value;
        };
    }
    return SliderElement;
}());

var DialElement = (function () {
    function DialElement(container, manager, name) {
        RackElement.call(this, container, manager, name);
        var self = this;
        container.innerHTML = '<div></div><canvas class="dial"></canvas>'
        this.text = container.children[0];
        this.dial = container.children[1];
        this.drawLine = function(ax,ay,bx,by) {
            this.context.moveTo(ax,ay);
            this.context.lineTo(bx,by);
            this.context.stroke();
        }
        this.context = this.dial.getContext("2d");
        this.redrawCanvas = function () {
            this.dial.width = this.dial.clientWidth;
            this.context.clearRect(0,0,this.dial.clientWidth,
                this.dial.clientHeight);
            this.context.strokeStyle = "#a6e22e";
            for(var i=0; i < 10; i++) {
                var x = (i * (this.dial.clientWidth / 10.0) + 
                    (this.value / this.max) * this.dial.clientWidth) %
                    this.dial.clientWidth;
                this.drawLine(x,0,x,this.dial.clientHeight);
            }
        }
        //this.dial.onresize = this.resizeCanvas;
        this.max = 100;
        this.sensitivity = 1;
        console.debug(container);
        var px = 0;
        this.dial.ontouchstart = function(e) {
            px = e.touches[0].clientX;
        }
        this.dial.ontouchmove = function(e) {
            var cx = e.touches[0].clientX;
            var dx = cx - px;
            px = cx;
            if (document.body.isMouseDown) {
                self.value += self.sensitivity * 
                    dx / self.dial.clientWidth;
                self.value %= self.max;
                if (self.value < 0) {
                    self.value = self.max + self.value;
                }
                self.onuserinput();
                self.redrawCanvas();
            }
        }
        this.dial.onmousemove = function(e) {
            if (document.body.isMouseDown) {
                self.value += self.sensitivity * 
                    e.movementX / self.dial.clientWidth;
                self.value %= self.max;
                if (self.value < 0) {
                    self.value = self.max + self.value;
                }
                self.onuserinput();
                self.redrawCanvas();
            }
        }
        this.onreceiveupdate = function () {
            this.text.innerText = this.value;
            this.redrawCanvas();
        };
    }
    return DialElement;
}());