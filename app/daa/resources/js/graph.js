(function() {
	
	var graph_container = null;
	var margin = {'top': 40, 'right': 20, 'bottom': 70, 'left': 100};
	var defaults = {'width': 500, 'height': 550};
	
	var colour = d3.scale.category20();

	function graphsize(graph) {
		var width = graph.width();
		var height = graph.height();
		//if(height == 0)
		height = defaults['height'];
		return {'height': height, 'width': width};
	}

	function segments(values) {
		var segments = [], i = 0, n = values.length;
		while(++i < n) {
			segments.push([[values[i - 1][0], values[i - 1][1]], [values[i][0], values[i][1]]]);
		}
		return segments;
	}

	function draw_line_graph(jg, data, type, time_period) {

		var size = graphsize(jg);
		var plotwidth = size['width']-margin['left']-margin['right'];
		var plotheight = size['height']-margin['top']-margin['bottom'];
		var plotpad = 20;

		var x = d3.scale.linear().domain([0, setup[time_period][1]]).range([0, plotwidth-margin['left']+margin['right']+plotpad]);
		var maxy = data.map(function(x) {
			var max = x['points'].reduce(function(p, c, i) {
				if(c[1] > p[1])
					return c;
				return p;
			});
			return max[1];
		});
		var miny = null;
		for(d in data) {
			var dt = data[d];
			var thismin = 0;
			if(dt['points'][0][1] < dt['points'][1][1]) {
				thismin = dt['points'][0][1];
			} else {
				thismin = dt['points'][1][1];
			}
			if('extrapolation' in dt) {
				var emin = 0;
				if(dt['extrapolation'][0][1] < dt['extrapolation'][1][1]) {
					emin = dt['extrapolation'][0][1];
				} else {
					emin = dt['extrapolation'][1][1]
				}
				if(emin < thismin) {
					thismin = emin;
				}
			}
			if(thismin < miny || miny == null) {
				miny = thismin;
			}
		}
        miny = miny-1;
		var y = d3.scale.linear().domain([miny, d3.max(maxy)]).range([plotheight-plotpad, 0]);

		var graphclass = type.replace(/ /g, '_')+"_"+time_period;

		graph = d3.select('#graph')
			.append('svg:svg')
			.attr('width', size['width']+'px')
			.attr('height', size['height']+'px')
			.attr('class', graphclass);

		$('.'+graphclass).before('<h2>'+type+'</h2>');

		// Plot group
		var pg = graph.append('svg:g')
			.attr('transform', 'translate('+margin['left']+', '+margin['top']+')');
		
		var eqline = d3.svg.line()
			.x(function(d, i) { return x(d[0]); })
			.y(function(d, i) { return y(d[1]); });

		var eqline_data = data.map(function(d) { return d.points });
		var extrp_data = data.map(function(d) { return d.extrapolation });

		var pe = pg.selectAll('g.extrp')
			.data(extrp_data)
			.enter().append('svg:g')
			.attr('class', 'extrp');

		var extrplines = pe.selectAll('path')
			.data(segments)
			.enter().append('svg:path')
			.attr('d', eqline)
			.attr('stroke', 'silver');

		var pl = pg.selectAll('g.line')
			.data(eqline_data)
			.enter().append('svg:g')
			.attr('class', 'line')
			.attr('style', function(d,i) { return 'color: '+colour(i) });
		
		var path = pl.selectAll('path')
			.data(segments)
			.enter().append('svg:path')
			.attr('d', eqline)
			.attr('stroke', 'currentColor')
			.attr('stroke-width', '2px');

		var circle = pl.selectAll('circle')
			.data(Object)
			.enter().append('svg:circle')
			.attr('cx', function(d, i) { return x(d[0]); })
			.attr('cy', function(d, i) { return y(d[1]); })
			.attr('r', 3)
			.attr('stroke-width', '2px')
			.attr('stroke', 'currentColor')
			.attr('fill', 'white');

		var label = pg.selectAll('g.plabel')
			.data(data)
			.enter()
			.append('svg:g')
			.attr('class', 'plabel')
			.append('svg:rect')
			.attr('x', function(d, i) { return x(d['points'][1][0])+15; })
			.attr('y', function(d, i) { return y(d['points'][1][1])-12; })
			.attr('width', function(d, i) { 
                var num_chars = d['percentage_change'].toString().replace('-', '').replace('.', '')+'%';
                return (num_chars.length+1.5)+'em' 
            })
			.attr('height', '1.5em')
			.attr('fill', function(d, i) { return colour(i) })
			.attr('stroke', function(d, i) { return colour(i) })
			.attr('stroke-width', 2)
		
		var labeltext = pg.selectAll('g.plabel')
			.data(data)
			.append('svg:text')
			.attr('x', function(d, i) { return x(d['points'][1][0])+20; })
			.attr('y', function(d, i) { return y(d['points'][1][1])+3; })
			.html(function(d, i) { 
                var label_text = '';
                if(d['percentage_change'].toString().substring(0,1) == '-') {
                    label_text = '&#x25bc; ';
                } else {
                    label_text = '&#x25b2; ';
                }
                return label_text+d['percentage_change'].toString().replace('-', '')+'%'  
            })

		d3.selectAll('g.plabel')
			.on('mouseover', function(d, i) { 
			})

		// Axis group
		var ag = graph.append('svg:g');

        /*
		// Axis lines
		// X Axis
		ag.append('svg:line')
			.attr('x1', margin['left']-plotpad)
			.attr('x2', plotwidth+(plotpad*2))
			.attr('y1', plotheight+plotpad)
			.attr('y2', plotheight+plotpad);

		// Y Axis
		ag.append('svg:line')
			.attr('x1', margin['left']-plotpad)
			.attr('x2', margin['left']-20)
			.attr('y1', plotheight+plotpad)
			.attr('y2', 0);
        */

		var xTicks = d3.svg.axis()
			.scale(x)
			.orient('bottom')
			.ticks(10);

		var yTicks = d3.svg.axis()
			.scale(y)
			.orient('left')
			.ticks(5);

		ag.append('svg:g')
			.attr('transform', 'translate(100, '+(plotheight+plotpad)+')')
			.call(xTicks);

		ag.append('svg:g')
			.attr('transform', 'translate('+(100-plotpad)+', 0)')
			.call(yTicks);

		ag.append('svg:text')
			.attr('x', plotwidth/2+30)
			.attr('y', plotheight+70)
			.text('Age ('+time_period+')');

		ag.append('svg:text')
			.attr('transform', 'rotate(-90)')
			.attr('x', -(plotheight/2)-30)
			.attr('y', 30)
			.text('Relative Value');
		
		// Legend group
		$('.'+graphclass).after('<div class="legend-container '+graphclass+'_legendcontainer"><h3>Legend</h3></div>');
		$('.'+graphclass+'_legendcontainer').append('<ul class="'+graphclass+'_legend legend"></ul>');

		var lg = d3.select('.'+graphclass+'_legend')
		var legendlabels = lg.selectAll('li')
			.data(data).enter()
			.append('li')
			.attr('style', function(d, i) { return 'color: '+colour(i); }) 
			.append('a')
			.attr('href', function(d, i) { return d.url })
			.html(function(d, i) { 
                var change_value = '<span class="legend_change_value '+d.type.toLowerCase()+'">'+d.percentage_change.toString()+'%</span>';
                var change_type = '<span class="legend_change_type '+d.type.toLowerCase()+'">'+d.type+' ('+d.process_measured+')</span>';
                return change_value+change_type+' <br> <span class="legend_change_name">'+d.name+'</span>';
            })
			.on('mouseover', function(d, i) {
				var selected = d3.select('.'+graphclass).selectAll('g.line').filter(function(d, j) { return j == i ? d : null });
				selected.selectAll('path, circle').transition().attr('stroke-width', '4px').attr('r', 4);
				var selected_label = d3.select('.'+graphclass).selectAll('g.plabel').filter(function(d, j) { return j == i ? d : null });
				selected_label.selectAll('text').transition().attr('style', 'font-weight: bold');
			})
			.on('mouseout', function(d,i) {
				var selected = d3.select('.'+graphclass).selectAll('g.line').filter(function(d, j) { return j == i ? d : null });
				selected.selectAll('path, circle').transition().attr('stroke-width', '2px').attr('r', 3);
				var selected_label = d3.select('.'+graphclass).selectAll('g.plabel').filter(function(d, j) { return j == i ? d : null });
				selected_label.selectAll('text').transition().attr('style', 'font-weight: normal');
			});
	}

	function draw_bar_graph(jg, data, type, time_period) {

		data.sort();

		var graphclass = type.replace(/ /g, '_')+"_"+time_period;

		var size = graphsize(jg);
		var plotwidth = size['width']-margin['left']-margin['right'];
		var plotheight = size['height']-margin['top']-margin['bottom'];
		var plotpad = 20;

		var points = []; //data.map(function(x) { return x.points });
		for(d=0; d<data.length; d++)
			points.push(data[d].points);

		var maxy = points.map(function(x) { return d3.max(x) });

		var labels = data[0].labels; 

		var x0 = d3.scale.ordinal().domain(d3.range(labels.length)).rangeBands([0, plotwidth], .2);
		var x1 = d3.scale.ordinal().domain(d3.range(data.length)).rangeBands([0, x0.rangeBand()]);
		var y = d3.scale.linear().domain([0, d3.max(maxy)]).range([plotheight, 0]); 

		var graph = d3.select('#graph')
			.append('svg:svg')
			.attr('class', 'svgraph '+graphclass)
			.attr('width', size['width']+'px')
			.attr('height', size['height']+'px')
			.append('svg:g')
			.attr('transform', 'translate(80,40)');

		$('.'+graphclass).before('<h2>'+type+'</h2>');

		// Columns
		var bars = graph.selectAll('g')
			.data(points)
			.enter().append('svg:g')
			.attr('fill', function(d,i) { return colour(i) })
			.attr("transform", function(d, i) { return 'translate('+x1(i)+', 0)'; });

		var rect = bars.selectAll('rect')
			.data(Object).enter()
			.append('svg:rect')
			.attr('transform', function(d,i) { return 'translate('+x0(i)+', '+plotheight+')'; })
			.attr('width', x1.rangeBand())
			.attr('height', function(d,i) { return plotheight - y(d) })
			.attr('y', function(d) { return y(d) - plotheight; });

		var values = bars.selectAll('text.values')
			.data(Object).enter()
			.append('svg:text')
			.attr('class', 'values')
			.attr('transform', function(d,i) { return 'translate('+x0(i)+', '+plotheight+')'; })
			.attr('x', x1.rangeBand() / 2)
			.attr('y', function(d,i) { return (y(d) - plotheight) - 20; })
			.attr('dy', '0.71em')
			.attr('text-anchor', 'middle')
			.text(function(d,i) { return d > 0 ? d : '' });

		var categories = graph.selectAll('text.categories')
			.data(d3.range(labels.length))
			.enter().append('svg:text')
			.attr('class', 'categories')
			.attr('class', 'group')
			.attr('transform', function(d,i) { return 'translate('+x0(i)+', 0)'; })
			.attr('x', x0.rangeBand() / 2)
			.attr('y', plotheight + 10)
			.attr('dy', '0.71em')
			.attr('text-anchor', 'middle')
			.text(function(d, i) { return labels[i] });

		var ag = graph.append('svg:g');

		// Axis lines
		// Y Axis

        /*
		ag.append('svg:line')
			.attr('x1', plotpad)
			.attr('x2', plotpad)
			.attr('y1', plotheight)
			.attr('y2', 0);
        */

		var yTicks = d3.svg.axis()
			.scale(y)
			.orient('left')
			.ticks(5);

		ag.append('svg:g')
			.attr('transform', 'translate('+(plotpad)+', 0)')
			.call(yTicks);

		ag.append('svg:text')
			.attr('x', plotwidth/2+30)
			.attr('y', plotheight+40)
			.text('Age ('+time_period+')');

		ag.append('svg:text')
			.attr('transform', 'rotate(-90)')
			.attr('x', -(plotheight/2)-60)
			.attr('y', -40)
			.text(data[0].process_measured+' '+data[0].measure);

		// Legend group
		$('.'+graphclass).after('<div class="legend-container '+graphclass+'_legendcontainer"><h3>Legend</h3></div>');
		$('.'+graphclass+'_legendcontainer').append('<ul class="'+graphclass+'_legend legend"></ul>');

		var lg = d3.select('.'+graphclass+'_legend')
		var legendlabels = lg.selectAll('li')
			.data(points).enter()
			.append('li')
			.attr('style', function(d, i) { return 'color: '+colour(i); }) 
			.append('a')
			.attr('href', function(d,i) { return data[i].url })
			.text(function(d, i) { return data[i].name });
	}

	function render_graph(graph_container, graphdata) {
		for(t in graphdata) {
			for(g in graphdata[t]) {
				for(p in graphdata[t][g]) {
					if(t == 'linear') {
						draw_line_graph(graph_container, graphdata[t][g][p], p, g);
					} else if(t == 'bar' || t == 'column') {
						draw_bar_graph(graph_container, graphdata[t][g][p], p, g);
					}
				}
			}
		}
	}

	//$('window').resize(function() { graph_container = $('#graph'); render_graph(graph_container, graphdata); });

	$('document').ready(function() {
		graph_container = $('#graph');
		render_graph(graph_container, graphdata);
	});

})();
