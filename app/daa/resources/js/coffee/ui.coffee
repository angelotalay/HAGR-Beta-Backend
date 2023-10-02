$(document).ready ->
	trees = $('.tissue-tree')
	if trees.length > 0
		trees.treeview collapsed: true	
		$.each(trees, ->
			$('.current', this).parentsUntil('.root').show()
		)
		trees.not('.visible').hide()

	rel_trees = $('.rel-tree')
	if rel_trees.length > 0
		rel_trees.treeview()
	
	$('.show-tree').toggle(
		-> 
			$(this).html('&#8679;').siblings('.root').show()
			return false
		, -> 
			$(this).html('&#8681;').siblings('.root').hide()
			return false
	)
