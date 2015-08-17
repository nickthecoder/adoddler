function request_progress()
{
    Net.post( {url: "/progressAjax", responseType: "text", onsuccess: update_progress });
}

function update_progress( result )
{
    var responses = result.responseText.split( " " );
    if (responses[0] != 'done') {

        var extruded = parseFloat(responses[0]);
        var total = parseFloat(responses[1]);

        var cm = Math.floor( extruded ) / 10;
        var text;
        if (cm > 100) {
            text = (cm / 100) + "m";
        } else {
            text = cm + "cm";
        }
        document.getElementById( "extrude_count" ).innerHTML = text;

        var width = (extruded / total * 100) + "%";
        document.getElementById( "progress_done" ).style.width = width;
    }

    if (responses[2] != 'None') {
        var text = "Extruder : " + responses[2] + "°C";
        document.getElementById( "extruder_temperature" ).innerHTML = text;
    }
}

setInterval(request_progress, 1000 * 10);

