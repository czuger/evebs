enable_tooltips = ->
  $('[data-toggle="tooltip"]').tooltip( { html: true } )
  return

# Test changes in javascript.
$(document).on('turbolinks:load', enable_tooltips )