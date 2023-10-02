(function($){
$(document).ready(function() {
    $('#lookup-gene').click(function() {
        $(this).siblings('span').remove();
        var value = $(this).siblings('input').attr('value');
        if (value != '') {
            $.get(this.href+value+'/', function(data) {
                for(field in data) {
                    if(field == 'species') {
                        options = $('[name="organism"] option').removeAttr('selected')
                        for(var o=0; o<options.length; o++) {
                            if(data['species'].search($(options[o]).text().toLowerCase()) != -1) {
                                $(options[o]).attr('selected', 'selected');
                            }
                        }
                    } else if(field == 'symbol') {
                        $('[name="symbol"]').attr('value', data[field]);
                        $('[name="gene_symbol"]').attr('value', data[field]);
                    } else if(field == 'name') {
                        $('[name="name"]').attr('value', data[field]);
                        $('[name="gene_name"]').attr('value', data[field]);
                    } else if(field == 'description') {
                        if($('[name="functions"]').length > 0 || $('[name="function"]').length > 0) {
                            $('[name="functions"]').attr('value', data[field]);
                            $('[name="function"]').attr('value', data[field]);
                        } else {
                            $('[name="description"]').attr('value', data[field]);
                        }
                    } else {
                        $('[name="'+field+'"]').attr('value', data[field]);
                    }
                }
            });
        } else {
            $('#lookup-gene').after('<span class="errornote inline-error gene-lookup-error">Please enter an Entrez Gene ID</span>')
        }
        return false;
    });
    /*$('#gene-lookup-spinner').ajaxStart(function() {
        $('#gene-lookup-error').hide();
        $(this).show();
    }).ajaxStop(function() {
         $('#gene-lookup-spinner').hide()
    });
    $('#gene-lookup-error').ajaxError(function(e, jqxhr, settings, exception) {
        $(this).show().text('There has been an error, please ensure the ID is correct and try again');
    });
    */

    $('#lookup-reference').click(function() {
        $(this).siblings('span').remove();
        var value = $(this).siblings('input').val();
        if (value != '') {
            $.get(this.href+value+'/', function(data) {
                for(field in data) {
                    $('[name="'+field+'"]').attr('value', data[field]);
                }
            });
        } else {
            $('#lookup-reference').after('<span class="errornote inline-error reference-lookup-error">Please enter a PubMed ID</span>')
        }
        return false;
    });
    /*
    $('#reference-lookup-spinner').ajaxStart(function() {
        $('#reference-lookup-error').hide();
        $(this).show();
    }).ajaxStop(function() {
         $('#reference-lookup-spinner').hide()
    });
    $('#reference-lookup-error').ajaxError(function(e, jqxhr, settings, exception) {
        $(this).show().text('There has been an error, please ensure the ID is correct and try again');
    });
    */

    $('#genage-human-lookup-details').click(function() {
        $(this).siblings('span').hide();
        var value = $(this).siblings('input').attr('value');
        var lookup_sections = ['uniprot', 'nucl', 'entrez', 'interactions'];
        if (value != '') {
            $('.lookup-widget').after('<span class="lookup-details-count">(<span class="lookup-details-current-count">0</span>/'+lookup_sections.length+' fetched)</span>');
            for(var l = 0; l < lookup_sections.length; l++) { 
                $.get(this.href+value+'/'+lookup_sections[l]+'/', function(data) {
                    var cc = parseInt($('.lookup-details-current-count').text());
                    $('.lookup-details-current-count').text(cc+1);
                    for(field in data) {
                        console.log(field, data[field]);
                        $('[name="'+field+'"]').attr('value', data[field]);
                    }
                    if(data.hasOwnProperty('interactions')) {
                        for(var i = 0; i<data['interactions'].length; i++) {
                            $('#hagrid_one-group .add-row a').trigger('click');
                            $('#id_hagrid_one-'+i+'-hagrid_two').attr('value', data['interactions'][i]);
                        }
                    }
                    if(data.hasOwnProperty('GO') && data['fetch_db_name'] == 'uniprot') {
                        console.log('GO HAS BEEEN TRIGGERED BY', data['fetch_db_name']);
                        for(var g = 0; g<data['GO'].length; g++) {
                            $('#go_set-group .add-row a').trigger('click');
                            var split_id = data['GO'][g]['id'].split(':');
                            console.log(data['GO'][g], data['GO'][g]['id']);
                            $('#id_go_set-'+g+'-go').attr('value', split_id[1]);
                            $('#id_go_set-'+g+'-name').attr('value', data['GO'][g]['term']);
                            $('#id_go_set-'+g+'-type').children('[value="'+data['GO'][g]['type']+'"]').attr('selected', 'selected');
                        }
                    }
                });
            }
        } else {
            $('.lookup-widget').after('<span class="errornote inline-error details-lookup-error">Please enter an Entrez Gene ID</span>')
        }
        return false;
    });
    /*
    $('#details-lookup-spinner').ajaxStart(function() {
        $('#details-lookup-error').hide();
        $(this).show();
    }).ajaxStop(function() {
         $('#details-lookup-spinner').hide()
    });
    $('#details-lookup-error').ajaxError(function(e, jqxhr, settings, exception) {
        $(this).show().text('There has been an error, please ensure the ID is correct and try again');
    });
    */

    $('.lookup-widget').ajaxStart(function() {
        $('#lookup-details-error').hide();
        $('#lookup-details-spinner').show();
        $('#lookup-details-spinner').css('display', 'inline-block');
    }).ajaxStop(function() {
         $('#lookup-details-spinner').hide();
    });
    $('#details-lookup-error').ajaxError(function(e, jqxhr, settings, exception) {
        $(this).show().text('There has been an error, please ensure the ID is correct and try again');
    });
});
})(django.jQuery);

