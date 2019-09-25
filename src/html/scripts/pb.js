var mURL = window.location.href;
mURL = mURL.replace('http:','ws:');
mURL = mURL.replace('/booth',"/ws-camera");
//pb-01:8888/ws-camera';
var ws = new WebSocket(mURL);
ws.onopen = function()
{
    // Web Socket is connected, send data using send()
    ws.send("Hello Test Camera");
    // ws.send(JSON.stringify({type:"Hello",data:"Hello Test"}));
    // alert("Message is sent...");
};
ws.onmessage = function (evt) {
    var re_data = evt.data;
    document.getElementById("pres").innerHTML = re_data;
}