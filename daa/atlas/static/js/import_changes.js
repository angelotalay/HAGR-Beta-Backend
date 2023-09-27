$(document).ready(function() {
    if(typeof IMPORT_DATA != "undefined" ) {
        var list = $('#changes-added');
        if(IMPORT_DATA['new'].length > 0) {
            add_to_database(IMPORT_DATA['new'][0], 0);
        }
    }
    function add_to_database(element, it) {
        var item = JSON.stringify(element);
        console.log(element);
        if(typeof item != 'undefined') {
            $.post(IMPORT_URL, {'csrfmiddlewaretoken': CSRF_TOKEN, 'item': item}, function(data, textStatus) {
                list.append('<li><a href="/admin/atlas/change/'+data['id']+'">'+data['identifier']+': '+data['name']+'</a></li>');
                if(it < IMPORT_DATA['new'].length) {
                    add_to_database(IMPORT_DATA['new'][it+1], it+1);
                }
                if(IMPORT_DATA['new'].length == it) {
                    $('#import-status').html('Import Finished');
                }
            }, 'json');
        }
    }
    $(document).ajaxError(function() { 
        $('#changes-added').append('<li class="error">There has been an error and some changes have not been imported.</li>');    
    });

});
