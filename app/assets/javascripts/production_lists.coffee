enable_production_list_management = ->
  $( '.shopping_basket_checkbox' ).change ->

    if $(this)[0].checked
      $.post '/production_lists/', { trade_hub_id: $(this).attr( 'trade_hub_id' ), eve_item_id: $(this).attr( 'eve_item_id' ) },
        error: (jqXHR, textStatus, errorThrown) ->
          console.log( "AJAX Error: #{textStatus}" )

    else
      $.post '/remove_production_list_check/', { trade_hub_id: $(this).attr( 'trade_hub_id' ), eve_item_id: $(this).attr( 'eve_item_id' ) },
        error: (jqXHR, textStatus, errorThrown) ->
          console.log( "AJAX Error: #{textStatus}" )

      if $(this).hasClass( 'delete_on_change' )
        $(this).parent().parent().remove()

$(document).on('turbolinks:load', enable_production_list_management )