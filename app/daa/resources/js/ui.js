(function() {
  $(document).ready(function() {
    var rel_trees, trees;
    trees = $('.tissue-tree');
    if (trees.length > 0) {
      trees.treeview({
        collapsed: true
      });
      $.each(trees, function() {
        return $('.current', this).parentsUntil('.root').show();
      });
      trees.not('.visible').hide();
    }
    rel_trees = $('.rel-tree');
    if (rel_trees.length > 0) {
      rel_trees.treeview();
    }
    return $('.show-tree').toggle(function() {
      $(this).html('&#8679;').siblings('.root').show();
      return false;
    }, function() {
      $(this).html('&#8681;').siblings('.root').hide();
      return false;
    });

  });
}).call(this);

$(document).ready(function() {
	$('.hidden-row').hide();
	var gotable = $('.go-table');
	var orthologtable = $('.ortholog-table');
	$('tfoot tr td', gotable).append('<a href="#" class="show-more-goterms"><span>&#x25bc;</span> Show more GO terms</a>');
	$('.show-more-goterms').toggle(function() { 
		$(this).html('<span>&#x25b2;</span> Hide GO terms'); 
		$('.hidden-row', gotable).show();
		return false;
	}, function(){
		$(this).html('<span>&#x25bc;</span> Show more GO terms'); 
		$('.hidden-row', gotable).hide();
		return false;
	});
	$('tfoot tr td', orthologtable).append('<a href="#" class="show-more-orthologs"><span>&#x25bc;</span> Show more orthologs</a>');
	$('.show-more-orthologs').toggle(function() { 
		$(this).html('<span>&#x25b2;</span> Hide orthologs'); 
		$('.hidden-row', orthologtable).show();
		return false;
	}, function(){
		$(this).html('<span>&#x25bc;</span> Show more orthologs'); 
		$('.hidden-row', orthologtable).hide();
		return false;
	});
});
