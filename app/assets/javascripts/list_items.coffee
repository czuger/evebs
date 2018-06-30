root = exports ? this

selectItem = ( node, check_state ) ->
  request = $.post '/choose_items/select_items', { id: node.internal_node_id, item: node.item, check_state: check_state }
  request.error (jqXHR, textStatus, errorThrown) ->
    $('#error_area').html(errorThrown)
    $('#error_area').show().delay(3000).fadeOut(3000);


setSelectItem = ->
  $('.item_checkbox').change ->
    console.log( $(this) )

    state = $(this).is(':checked')
    id = $(this).attr('item_id')

    request = $.post '/choose_items/select_items', { id: id, item: true, check_state: true }

    request.error (jqXHR, textStatus, errorThrown) ->
      $('#error_area').html(errorThrown)
      $('#error_area').show().delay(3000).fadeOut(3000);


$(document).on('turbolinks:load'
  ->
    if window.location.pathname.match( /list_items\/edit/ )
      console.log( 'loaded' )
      setSelectItem()
)