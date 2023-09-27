var previous_tissue = '';
var float_label = $('#float-label');
float_label.hide();

function show_label(tissue) {
	float_label.show();
	var tissue_details = tissues[tissue]
    var change_count = tissue_details['type_changes_count'];
    change_count_list = '<ul class="label-types">';
    for(var i=0; i<change_count.length; i++) {
        console.log(change_count[i]);
        change_count_list += '<li><a href="'+tissue_details['url']+'&type='+change_count[i]['type']+'" class="'+change_count[i]['type']+'-type">'+change_count[i]['type__count']+'</a></li>';
    }
    change_count_list += '</ul>';
	float_label.html('<span class="label-title">'+tissue+'</span><span class="label-synonyms">'+tissue_details['synonyms']+'</span><a class="label-changes" href="'+tissue_details['turl']+'">'+tissue_details['number_of_changes']+' <span>changes &#x27a5;</span></a>'+change_count_list);
}

function click_label(tissue) {
	var tissue_details = tissues[tissue];
	window.location.href = tissue_details['turl'];
}

function hide_label() {
}

$(document).ready(function() {

	$('#float-label').jScroll({speed : "fast"});

	$('.tissue-tree > li').addClass('collapsable lastCollapsable').removeClass('expandable lastExpandable').children('ul').first().show().children('div').first().addClass('lastCollapsable-hitarea collapsable-hitarea');

	$.extend($.expr[':'], {
		'containsi': function(elem, i, match, array)
		{
			return (elem.textContent || elem.innerText || '').toLowerCase().indexOf((match[3] || "").toLowerCase()) >= 0;
		}
	});

	$('#filter-tissues').keyup(function(){
		$('#filter-tissues-results').empty();
		var filter_value = $('#filter-tissues').attr('value');
		if(filter_value.length > 2) {
			var matching_li = $('.tissue-tree li:containsi("'+filter_value+'")').clone().find('div, ul, li').remove().end().filter(':containsi("'+filter_value+'")');
			$('#filter-tissues-results').empty().append(matching_li);
		}
	});
	
	$('#filter-tissues-results li').live('click', function(){
		var text = $('span', this).text();
		//$('.tissue-tree li:contains("'+text+'"):last').children('span').addClass('highlight').end().parents().addClass('collapsable').removeClass('expandable').css({display: 'block'});
		$('.tissue-tree li:contains("'+text+'"):last').children('span').addClass('highlight');
		$('.tissue-tree li:contains("'+text+'"):last').parentsUntil('.root', 'ul, li').addClass('collapsable').removeClass('expandable').show().children('div').addClass('collapsable-hitarea').removeClass('expandable-hitarea');
	});

});
