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
    console.log(typeof evt.data);
    var received_msg = JSON.parse(re_data);
    if ( received_msg['type'] == 'countdown') {
        document.getElementById("countdown").innerHTML = received_msg['data'];
        document.getElementById("baseID").innerHTML = "";
    }
    else if (received_msg['type'] == 'hello') {
        document.getElementById("baseID").innerHTML = received_msg['data'];
    }
    else if (received_msg['type'] == 'photo') {
        tmp_output =  "<a href='../booth'>Snap Another?</a><br /><br />";
        tmp_output +=  "<img src='" + received_msg['data'] + "'><br />";
        document.getElementById("countdown").innerHTML = "";
        document.getElementById("baseID").innerHTML = tmp_output;
    }
    else if ( received_msg['type'] == 'update') {
        var image = new Image();
        image.src = 'data:image/png;base64,' + received_msg['data']['imgData'];
        document.body.appendChild(image);
        document.getElementById("countdown").innerHTML = received_msg['data']['msg'];
        // document.getElementById("imgView").innerHTML = "<img src='";
    }
    else {
        document.getElementById("baseID").innerHTML = received_msg['data'];
    }
}