/* Created by: Thomas Craig
*/

String.prototype.format = function() {
	var args = arguments;
	return this.replace(/{(\d+)}/g, function(match, number) { 
		return typeof args[number] != 'undefined' ? args[number]: match;
	});
};

(function( $ ) {
	$.fn.queryBuilder = function(options) {
		
		var FIELD_OPERATIONS = {
			'text': {
				'exact': 'exactly',
				'icontains': 'containing',
				'istartswith': 'begining with',
				'iendswith': 'ending with'
			},
			'number': {
				'exact': 'exactly',
				'gt': 'greater than',
				'lt': 'less than'
			}
		}

		var FILTER_TEMPLATE = '<li><select class="field_list">{0}</select> is <select class="operations_list">{1}</select> {2} {3} <a href="#" class="button add-filter">+</a></li>';
		var REMOVE_TEMPLATE = '<a href="#" class="button remove-filter">-</a>';

		var opts = {
			'operations': FIELD_OPERATIONS,
			'fields': {},
			'prefix_strip': [],
			'active_fields': [],
			'template': FILTER_TEMPLATE,
			'remove_template': REMOVE_TEMPLATE
		}

		if (options) { 
			$.extend(opts, options);
		}

		var sfields = []
		for(var k in opts.fields) sfields.push(k);
		sfields.sort();

		function generateFieldOptions(fields, selectedField) {
			var field_options = '<option value="">Select something to filter</option>';
			$.each(sfields, function(index, value){
				index = value;
				value = opts.fields[value];
				if(value.active != 'True' || selectedField == index) {
					if(selectedField == index){
						selected = 'selected="selected"';
					} else {
						selected = '';
					}
					var names = index.split('__')
					var trim_name = names[names.length-1] 
					if(names.length > 1 && $.inArray(names[names.length-2], opts.prefix_strip) == -1)
						trim_name = names[names.length-2]+' '+names[names.length-1]
					field_options += '<option '+selected+' value="'+index+'">'+trim_name.replace(/_/g, ' ')+'</option>';
				}
			});
			return field_options;
		}

		function generateOperationOptions(operations, type, selectedOperation) {
			if(type == 'DateField' || type == 'NumberField' || type == 'DecimalField' ) {
				operations = operations.number
			} else if (type == 'CharField') {
				operations = operations.text
			} else {
				operations = {}
			}
			field_operations = '';	
			$.each(operations, function(index, value) {
				var selected = '';
				if(index == selectedOperation) {
					selected = 'selected="selected"';
				}
				field_operations += '<option '+selected+' value="'+index+'">'+value+'</option>';
			});
			return field_operations
		}

		function generateWidget(fields, fieldName) {
			return fields[fieldName]['widget']
		}

		function updateFieldChoices(fields) {
			field_options = $('.field_list');
			$.each(field_options, function(index, value) {
				current_selection = $(value).val()
				$(value).html(generateFieldOptions(fields, current_selection))
			});
		}

		function initFeatures(fieldName, fieldType) {
			var toAction = $('[name="'+fieldName+'"]', '.filter-item'); 
			toAction.parent().children('.field_list').data('old', fieldName);
			toAction.parent().children('.operations_list').show();
			toAction.parent().children('.operations_list').attr('name', 'lookups['+fieldName+']');
			if(fieldType == 'DateField') {
				toAction.datepicker({dateFormat: 'dd/mm/yy'});
			} else if (fieldType == 'ModelMultipleChoiceField') {
				toAction.parent().children('.operations_list').hide();
				toAction.parent().children('.operations_list').attr('name', '');
				toAction.multiselect().multiselectfilter();	
			} else if (fieldType == 'ModelChoiceField' || fieldType == 'ChoiceField') {
				toAction.parent().children('.operations_list').hide();
				toAction.parent().children('.operations_list').attr('name', '');
			} else if (fieldType == 'BooleanField' || fieldType == 'NullBooleanField') {
				toAction.parent().children('.operations_list').hide();
				toAction.parent().children('.operations_list').attr('name', '');
			}
		}	

		function createFilter(target, opts, fieldName) {
			if(fieldName == '') {
				for(obj in opts.fields) {
					if(opts.fields[obj].active != 'True') {
						fieldName = obj;
						break;
					}
				}
			}
			if(fieldName != '') {
				remove = '';
				if($(target).children('li').length > 0){
					remove = opts.remove_template;
				}
				filter = opts.template.format(generateFieldOptions(opts.fields, fieldName), generateOperationOptions(opts.operations, opts.fields[fieldName].type,  opts.fields[fieldName].lookup), generateWidget(opts.fields, fieldName), remove);
				target.append(filter);
				opts.fields[fieldName].active = 'True';
				initFeatures(fieldName, opts.fields[fieldName].type);
				updateFieldChoices(opts.fields);
			}
		}

		function alterFilter(location, opts, fieldName, oldField) {
			opts.fields[oldField].active = 'False';
			var op_list = $('.operations_list', $(location).parent())
			op_list.html(generateOperationOptions(opts.operations, opts.fields[fieldName].type, opts.fields[fieldName].lookup));
			op_list.next('input, select').remove()
			op_list.after(generateWidget(opts.fields, fieldName));
			initFeatures(fieldName, opts.fields[fieldName].type)
			opts.fields[fieldName].active = 'True';
			updateFieldChoices(opts.fields);
		}

        $('.add-specific-filter').live('click', {'target': this, 'opts': opts}, function(event){
            var filter_for = $(this).data('filter-for');
            var filter_value = $(this).data('filter-value');
            if($('.filter-item').length == 1) {
                var loc = $('.filter-form ul li:first-child');
                $('.field_list', loc).val('type').trigger('change');
                $('[name="'+filter_for+'"]', loc).val(filter_value).trigger('change');
            } else { 
                if($('[name="'+filter_for+'"]').length > 0) {
                    var loc = $('[name="'+filter_for+'"]', '.filter-form').parent();
                    $('.field_list', loc).val('type').trigger('change');
                    $('[name="'+filter_for+'"]', loc).val(filter_value).trigger('change');
                } else {
			        createFilter(event.data.target, event.data.opts, filter_for, {}); 
                }
            }
            $('.filter-form').submit();
			return false;
		});
		
		$('.add-filter').live('click', {'target': this, 'opts': opts}, function(event){
			createFilter(event.data.target, event.data.opts, '', {}); 
			return false;
		});
		
		$('.field_list').live('change', {'opts': opts}, function(event){
			alterFilter(this, opts, $(this).val(), $(this).data('old'));
			$(this).data('old', $(this).val());
			return false;
		});

		$('.remove-filter').live('click', {'target': this, 'opts': opts}, function(event){
			deactive = $(this).parent().children('.field_list').val();
			$(event.currentTarget).parent().remove();
			event.data.opts.fields[deactive].active = 'False';
			updateFieldChoices(opts.fields);
			return false;
		});

		var active = 0;
		var target = this;
		$.each(opts.fields, function(index, value) {
			if(value.active == 'True') {
				createFilter(target, opts, index, opts.fields[index]);
				active++;
			}
		});
		if(active < 1) {
			createFilter(this, opts, '', {});
		}
	};
})(jQuery);
