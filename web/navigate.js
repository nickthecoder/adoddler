// Changes the navigate buttons and the extrude buttons to use ajax
function convert_navigation()
{
    var buttons = document.getElementsByTagName("button");
    for (i = 0; i < buttons.length; i ++ ) {
        button = buttons[i];
        if ( button.className.indexOf( "small" ) >= 0 ) {
            convert_button( button );
        }
    }
}
function convert_button( button )
{
    button.onclick = function() {
        Net.post( {url: "/gcodeAjax", responseType: "text", vars: {gcode: button.value}, onsuccess: gcodeok });
        return false;
    }
}
function gcodeok( result )
{
    if ( result.responseText ) {
        alert( result.responseText );
    }
}
window.onload=convert_navigation;

