$(document).ready ->

  console.log( 'Filters on' )

  $( '#select_trade_hubs' ).change ->
    selected_value = $(this).val()
    $('.trade_hub_name').parent().show()

    if selected_value != ''
      $('.trade_hub_name')
      .filter ->
        $( this ).html() != selected_value
      .parent().hide()


  $( '#select_items' ).change ->
    selected_value = $(this).val()
    $('.item_name').parent().show()

    if selected_value != ''
      $('.item_name')
      .filter ->
        $( this ).children().html() != selected_value
      .parent().hide()
