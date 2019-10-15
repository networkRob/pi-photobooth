var mURL = window.location.href;
mURL = mURL.replace('http:','ws:');
mURL = mURL.replace('/booth',"/ws-camera");
//pb-01:8888/ws-camera';
var ws = new WebSocket(mURL);
ws.onopen = function()
{
    // Web Socket is connected, send data using send()
    ws.send(JSON.stringify({type:"hello",data:"Hello Test Camera"}));
};
ws.onmessage = function (evt) {
    var re_data = evt.data;
    var received_msg = JSON.parse(re_data);
    if (received_msg['type'] == 'hello') {
        document.getElementById("baseID").innerHTML = received_msg['data'];
    }
    // Countdown messages displayed
    else if ( received_msg['type'] == 'countdown') {
        document.getElementById("countdown").innerHTML = received_msg['data'];
        document.getElementById("baseID").innerHTML = "";
        document.getElementById("title").innerHTML = "Get Ready!";
    }
    // Intermediate photo displayed
    else if ( received_msg['type'] == 'update') {
        document.getElementById("countdown").innerHTML = received_msg['data']['msg'];
        document.getElementById("title").innerHTML = "";
        document.getElementById("imgView").innerHTML = "<img src='data:image/png;base64," + received_msg['data']['imgData'] + "'/><br />";
    }
    // Final photostrip displayed
    else if (received_msg['type'] == 'photo') {
        tmp_output =  "<a href='../booth'>Snap Another?</a>";
        tmp_output += "<form action='javascript:void(0);'>Print More? <input type='number' value='1' id='pcopy' min='1' max='3'> <input type='button' value='Print More!' onclick='printMore()'></form> "
        tmp_output += "<br /><br />";
        document.getElementById("imgView").innerHTML =  "<img src='" + received_msg['data'] + "'><br />";
        document.getElementById("countdown").innerHTML = "";
        document.getElementById("baseID").innerHTML = tmp_output;
        document.getElementById("title").innerHTML = "";
    }
    else {
        document.getElementById("baseID").innerHTML = received_msg['data'];
    }
}
function printMore() {
    // Function to request more printed copies
    ws.send(JSON.stringify({type:"print",data:document.getElementById("pcopy").value}));
}