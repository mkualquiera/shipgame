
function buildRequest(rtype, rpath, rpayload) {
    return JSON.stringify({ type: rtype, path: rpath, payload: rpayload });
}
var HueEntry = (function () {
    function HueEntry(sync, value, path) {
        this.path = path;
        this.value = value;
        this.sync = sync;
        this.onget = function () { };
        this.onvaluechange = function () { };
    }
    HueEntry.prototype.sendValue = function () {
        this.sync.ws.send(buildRequest("SET", this.path, this.value));
    };
    HueEntry.prototype.handleGet = function () {
        this.onget(this);
        this.sendValue();
    };
    HueEntry.prototype.setValue = function (value) {
        this.value = value;
        this.sendValue();
        this.onvaluechange(this);
    };
    HueEntry.prototype.handleSet = function (value) {
        this.value = value;
        this.onvaluechange(this);
    };
    HueEntry.prototype.subscribe = function () {
        this.sync.ws.send(buildRequest("SUB", this.path, ""));
    };
    return HueEntry;
}());
var HueSync = (function () {
    function HueSync(addr) {
        this.ws = new WebSocket(addr);
        var self = this;
        this.ws.onmessage = function (e) {
            var req_obj = JSON.parse(e.data);
            if (typeof (self.database[req_obj.path]) == "undefined") {
                self.database[req_obj.path] = new HueEntry(self, req_obj.value, req_obj.path);
            }
            if (req_obj.type == "SET") {
                self.database[req_obj.path].handleSet(req_obj.payload);
            }
            if (req_obj.type == "GET") {
                self.database[req_obj.path].handleGet();
            }
        };
        this.database = {};
    }
    HueSync.prototype.subscribe = function (path, callback) {
        if (typeof (this.database[path]) == "undefined") {
            this.database[path] = new HueEntry(this, "", path);
        }
        this.database[path].subscribe();
        this.database[path].onvaluechange = callback;
        return this.database[path];
    };
    return HueSync;
}());
