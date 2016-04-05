$(document).ready ->
  autocomplete = $( '#add-items-autocomplete' )

  console.log( autocomplete )

  autocomplete.autocomplete
    source: '/choose_items/autocomplete_eve_item_name_lowcase'
    minLength: 2
    appendTo: '#autocomplete_result'
    select: (event, ui) ->
      console.log if ui.item then 'Selected: ' + ui.item.value + ' aka ' + ui.item.id else 'Nothing selected, input was ' + @value
      return false
    focus: () ->
      console.log( 'Got focus' )
      return false
