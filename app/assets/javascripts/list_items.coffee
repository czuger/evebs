setSelectItem = ->
  $('.item_checkbox').change ->
    console.log( $(this) )

    state = $(this).is(':checked')
    id = $(this).attr('item_id')

    request = $.post '/list_items/selection_change', { id: id, item: true, check_state: state }

    request.fail (jqXHR, textStatus, errorThrown) ->
      $('#error_area').html(errorThrown)
      $('#error_area').show().delay(3000).fadeOut(3000);

$(document).on('turbolinks:load'
  ->
    if window.location.pathname.match( /list_items/ )
      console.log( 'loaded' )
      setSelectItem()
)