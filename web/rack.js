

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
        console.debug(container);
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