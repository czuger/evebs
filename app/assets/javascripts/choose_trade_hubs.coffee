root = exports ? this

selectTradeHub = ( node, check_state ) ->
  $.ajax
    type: 'PATCH'
    url: '/choose_trade_hubs'
    data:
      id: node
      check_state: check_state

checkTradeHubList = ->

  return unless $( '#choose_trade_hub' ).val() == 'true'

  $('.trade_hub_update_checkbox').change ->
    selectTradeHub( $(this).val(), $(this).prop('checked') )

$(document).on('turbolinks:load', checkTradeHubList )

