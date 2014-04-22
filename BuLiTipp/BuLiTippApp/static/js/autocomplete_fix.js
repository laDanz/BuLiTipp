$('#id_fuer-autocomplete').bind('selectChoice', function(e, choice, autocomplete) {

	$('#id_fuer-autocomplete').val(choice.text());
	var hidden_input = $("<input type='hidden' id='id_fuer-autocomplete-hidden' name='user_select' value='"+choice.data().value+"'>");
	$('#id_fuer-autocomplete').append(hidden_input)
	$('#id_fuer-autocomplete').change(function(e) {
		$('#id_fuer-autocomplete-hidden').remove();
	});

});

yourlabs.Widget.prototype.selectChoice = function(e, choice, autocomplete) {
	// override default selectChoice behavior 
	return;

};