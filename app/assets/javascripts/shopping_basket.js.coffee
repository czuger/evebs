set_shopping_basket = ->
  $( '.shopping_basket_checkbox' ).change ->
    console.log( $(this).parent() )

    button = 
    $.post '/price_advices/update_basket/', { item_code: $(this).val(), checked: $(this)[0].checked }
    if $(this).hasClass( 'delete_on_change' )
      $(this).parent().parent().remove()

$(document).on('turbolinks:load', set_shopping_basket )