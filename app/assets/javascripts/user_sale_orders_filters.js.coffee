params = {}

process_user_sale_orders_filters = ( selector_id, selector_value ) ->
  params['trade_hub_id'] = $( "#select_trade_hubs" ).val() if $( "#select_trade_hubs" ).val()
  params['eve_item_id'] = $( "#select_items" ).val() if $( "#select_items" ).val()

  window.location.href = window.location.pathname + "?#{$.param(params)}"

set_user_sale_orders_filters = ->

  $( '#select_trade_hubs' ).change ->
    process_user_sale_orders_filters( 'th', $(this) )

  $( '#select_items' ).change ->
    process_user_sale_orders_filters( 'ei', $(this) )

$(document).on('turbolinks:load'
  ->
    if window.location.pathname.match( /user_sale_orders/ )
      set_user_sale_orders_filters()
)

