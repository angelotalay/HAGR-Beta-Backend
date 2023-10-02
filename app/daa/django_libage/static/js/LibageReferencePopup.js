function showLibageReferencePopup(triggeringLink, identifier_name, name_fields, source_id) {
    var name = triggeringLink.id;
    name = id_to_windowname(name);
    var identifier = document.getElementById(identifier_name).value;
    var entry_name = ''
    for(var f in name_fields) {
        entry_name += document.getElementById(name_fields[f]).value;
        if(f < name_fields.length-1) {
            entry_name += ', '
        }
    }
    var href = triggeringLink.href+'&identifier='+identifier+'&title='+entry_name+'&source='+source_id;
    var win = window.open(href, name, 'height=500,width=800,resizable=yes,scrollbars=yes');
    win.focus();
    return false;
}

function dismissLibageReferencePopup(win, newId, refs) {
    newId = html_unescape(newId);
    //newRepr = html_unescape(newRepr);
    var name = windowname_to_id(win.name);
    var elem = document.getElementById(name);
    var refList = document.getElementById(name+'_reflist');
    refList.innerHTML = refs; 
    elem.href = elem.href.replace('add/?_popup=1', newId+'/?_popup=1');
    win.close();
}
