
$('document').ready(function(){

	data.sort();

	var x = d3.scale.linear().domain([0, d3.max(data.map(function(x){ return x[1]; }))]).range([0, 420]); 
	var y = d3.scale.ordinal().domain(data.map(function(x){ return x[0]; })).rangeBands([0, 205]);

	var chart = d3.select('#chart')
		.append('svg:svg')
		.attr('class', 'svgchart')
		.attr('width', '100%')
		.attr('height', 250)
		.append('svg:g')
		.attr('transform', 'translate(100,50)');

	chart.append('text')
		.attr('transform', 'rotate(-90)')
		.attr('dx', -100)
		.attr('dy', -60)
		.text('Age')

	chart.append('text')
		.attr('dx', '26em')
		.attr('dy', '-2.8em')
		.attr('text-anchor', 'middle')
		.text(data_measure)

	// Tick lines
	chart.selectAll('line')
		.data(x.ticks(10))
		.enter().append('svg:line')
		.attr('x1', x)
		.attr('x2', x)
		.attr('y1', -5)
		.attr('y2', '100%')
		.attr('stroke', '#ccc');

	// Columns
	chart.selectAll('rect')
		.data(data.map(function(x){ return x[1] }))
		.enter().append('svg:rect')
		.attr('fill', 'steelblue')
		.attr('fill-opacity', 0.8)
		.attr('y', function(d,i) { return (y.rangeBand()-2) * i})
		.attr('width', x)
		.attr('height', y.rangeBand()-2);

	// Values of the columns
	chart.selectAll('text.value')
		.data(data.map(function(x){ return x[1] }))
		.enter().append('svg:text')
		.attr('class', 'value')
		.attr('x', x)
		.attr('y', function(d,i) { return (y.rangeBand()-2) * i }) //y(d) + y.rangeBand() / 2; })
		.attr('dx', '0.5em')
		.attr('dy', '1.25em')
		.attr('text-anchor', 'start')
		.text(String);

	// Tick labels
	chart.selectAll('text.rule')
		.data(x.ticks(10))
		.enter().append('svg:text')
		.attr('class', 'rule')
		.attr('x', x)
		.attr('y', '-0.5em')
		.attr('dy', -3)
		.attr('text-anchor', 'middle')
		.text(String);

	// Column labels
	chart.selectAll('text.label')
		.data(data.map(function(x){ return x[0] }))
		.enter().append('svg:text')
		.attr('class', 'label')
		.attr('x', -8)
		.attr('y', function(d,i) { return (y.rangeBand()-2) * i })//y)
		.attr('dy', '1.5em')//'1.8em')
		.attr('text-anchor', 'end')
		.text(String)

	chart.append('svg:line')
		.attr('y1', -5)
		.attr('y2', '100%')
		.attr('stroke', '#000');

});
