enable_production_list_management = ->
  $( '.shopping_basket_checkbox' ).change ->

    if $(this)[0].checked
      $.post '/production_lists/', { trade_hub_id: $(this).attr( 'trade_hub_id' ), eve_item_id: $(this).attr( 'eve_item_id' ) }

    else

      $.ajax "/production_lists/#{$(this).val()}",
        type: 'DELETE'
        error: (jqXHR, textStatus, errorThrown) ->
          console.log( "AJAX Error: #{textStatus}" )
        success: (data, textStatus, jqXHR) ->
          console.log( "Successful AJAX call: #{data}" )

      if $(this).hasClass( 'delete_on_change' )
        $(this).parent().parent().remove()

$(document).on('turbolinks:load', enable_production_list_management )