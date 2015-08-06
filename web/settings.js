var cancelSetting;
var saveSetting;
var edittingEle;

function editSetting( ele, code, letter )
{
    if ( edittingEle == ele ) {
        return true;
    }

    if ( edittingEle ) {
        cancelSetting();
        cancelSetting = null;
        edittingEle = null
    }

    edittingEle = ele

    var input = document.createElement("input");
    var oldValue = ele.innerHTML;
    input.value = oldValue;
    input.type = 'text';
    input.size = 6;

    ele.innerHTML = '';

    ele.appendChild(input);
    input.focus();

    var okcancel = document.getElementById( 'okcancel' )
    ele.parentNode.appendChild(okcancel);
    okcancel.style.display = 'block';

    cancelSetting = function() {
        ele.innerHTML = oldValue;
        okcancel.style.display = 'none';
        edittingEle = null;
    }

    saveSetting = function() {
        newValue = parseFloat( input.value );
        cancelSetting();
        ele.innerHTML = 'saving...';

        onsaved = function( result ) {
            ele.innerHTML = result.responseText;
        }
        Net.post( {url: "/changeSettingAjax", responseType: "text", vars: {code: code, letter: letter, value: newValue}, onsuccess: onsaved });
    }
}

