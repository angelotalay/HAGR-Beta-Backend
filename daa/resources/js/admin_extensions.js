(function($) {
	$(document).ready(function() {
		
		$('.selectable-rawid-choices').live('change', function() {
			var chosen = $(this).attr('value');
			$(this).next('a').attr('href', '../../../atlas/'+chosen+'/?t=id');
		});

	});
})(django.jQuery)
