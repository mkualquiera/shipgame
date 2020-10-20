
function buildRequest(rtype :string, rpath:string, rpayload: any) : string {
  return JSON.stringify({type: rtype, path: rpath, payload: rpayload})
}

class HueEntry {
  value: any;
  path: string;
  sync: HueSync;
  onget : Function;
  onvaluechange: Function;
  constructor(sync: HueSync, value: any, path: string) {
    this.path = path;
    this.value = value;
    this.sync = sync;
    this.onget = function() {};
    this.onvaluechange = function() {};
  }
  sendValue() {
    this.sync.ws.send(buildRequest("SET",this.path,this.value));
  }
  handleGet() {
    this.onget(this);
    this.sendValue();
  }
  setValue(value: any) {
    this.value = value;
    this.sendValue();
    this.onvaluechange(this);
  }
  handleSet(value: any) {
    this.value = value;
    this.onvaluechange(this);
  }
  subscribe() {
    this.sync.ws.send(buildRequest("SUB",this.path,""));
  }
}

class HueSync  {
  ws: WebSocket;
  database: any;
  constructor(addr : string) {
    this.ws = new WebSocket(addr);
    var self = this;
    this.ws.onmessage = function(e) {
      var req_obj = JSON.parse(e.data);
      if (typeof(self.database[req_obj.path]) == "undefined") {
        self.database[req_obj.path] = new HueEntry(self,req_obj.value,req_obj.path);
      }
      if (req_obj.type == "SET") {
        self.database[req_obj.path].handleSet(req_obj.payload);
      }
      if (req_obj.type == "GET") {
        self.database[req_obj.path].handleGet();
      }
    }
    this.database = {};
  }
  subscribe(path:string, callback: Function) {
    if (typeof(this.database[path]) == "undefined") {
      this.database[path] = new HueEntry(this,"",path);
    }
    this.database[path].subscribe()
    this.database[path].onvaluechange = callback;
    return this.database[path];
  }
}