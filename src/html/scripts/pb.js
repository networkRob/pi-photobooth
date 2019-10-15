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
        document.getElementById("title").innerHTML = "";
        document.getElementById("msgUpdate").innerHTML = received_msg['data'];
        document.getElementById("countdown").innerHTML = "";
        document.getElementById("baseID").innerHTML = "";
        document.getElementById("imgView").innerHTML =  "";
    }
    // Pre Countdown
    else if ( received_msg['type'] == 'ready') {
        document.getElementById("title").innerHTML = "Get Ready!";
        document.getElementById("msgUpdate").innerHTML = received_msg['data'];
        document.getElementById("countdown").innerHTML = ""
        document.getElementById("baseID").innerHTML = "";
        // document.getElementById("imgView").innerHTML = "";
    }
    // Countdown messages displayed
    else if ( received_msg['type'] == 'countdown') {
        document.getElementById("title").innerHTML = "";
        // document.getElementById("msgUpdate").innerHTML = received_msg['data'];
        document.getElementById("countdown").innerHTML = received_msg['data'];
        document.getElementById("baseID").innerHTML = "";
        document.getElementById("imgView").innerHTML = "";
    }
    // Intermediate photo displayed
    else if ( received_msg['type'] == 'update') {
        document.getElementById("title").innerHTML = "";
        document.getElementById("msgUpdate").innerHTML = received_msg['data']['msg'];
        document.getElementById("countdown").innerHTML = "";
        document.getElementById("baseID").innerHTML = "";
        document.getElementById("imgView").innerHTML = "<img src='data:image/png;base64," + received_msg['data']['imgData'] + "'/><br />";
    }
    // Done taking pictures
    else if ( received_msg['type'] == 'done') {
        document.getElementById("title").innerHTML = "";
        document.getElementById("msgUpdate").innerHTML = received_msg['data'];
        document.getElementById("countdown").innerHTML = "";
        document.getElementById("baseID").innerHTML = "";
        document.getElementById("imgView").innerHTML = "";
    }
    // Final photostrip displayed
    else if (received_msg['type'] == 'photo') {
        tmp_output =  "<a href='../booth'>Snap Another?</a><br /><br />";
        tmp_output += "<p><form action='javascript:void(0);'>Print More Copies? (1 - 3)<br /> <input type='number' value='1' id='pcopy' min='1' max='3'> <a onclick='printMore()'>Print More!</a></form></p>"
        tmp_output += "<br /><br />";
        document.getElementById("title").innerHTML = "";
        document.getElementById("msgUpdate").innerHTML = "";
        document.getElementById("countdown").innerHTML = "";
        document.getElementById("baseID").innerHTML = tmp_output;
        document.getElementById("imgView").innerHTML =  "<img src='" + received_msg['data'] + "'><br />";
    }
    else {
        document.getElementById("baseID").innerHTML = received_msg['data'];
    }
}
function printMore() {
    // Function to request more printed copies
    ws.send(JSON.stringify({type:"print",data:document.getElementById("pcopy").value}));
}