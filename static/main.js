function main() {
    $.getJSON("figures.json", function(data) {
	$.each(data.figures, function(figure_name, figure_meta) {
	    new_divs = ''
	    counter = 0
	    width = $('#' + figure_name).width()
	    offset = $('#' + figure_name).offset()
	    $.map(figure_meta.labels, function(label_meta) {
		x = label_meta.insert[0] + offset.left
		y = label_meta.insert[1] + offset.top
		new_divs += '<div class="rasm_' + label_meta.alignment + '" id="' + figure_name + '_label_' + counter + '" style="position:absolute; top:' + y + 'px; left:' + x + 'px; font-size:15xpx;">'
		new_divs += label_meta.text + '</div>'
		counter += 1
	    })
	    res = $('#' + figure_name).append(new_divs)
	    for (var i = 0; i < counter; i++) {
		id = figure_name + '_label_' + i
		MQ.StaticMath(document.getElementById(id));
	    }
	    $('.rasm_middle').map(function(i, div) {
		obj = $('#' + div.id)
		offset = obj.offset()
		console.log(offset)
		obj.css('left', (offset.left - obj.width() / 2) + "px")
	    })
	    $('.rasm_end').map(function(i, div) {
		obj = $('#' + div.id)
		offset = obj.offset()
		obj.css('left', (offset.left - obj.width() / 2) + "px")
	    })
	})
    })
}
