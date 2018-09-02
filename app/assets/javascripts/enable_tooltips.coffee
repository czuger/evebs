enable_tooltips = ->
  $('[data-toggle="tooltip"]').tooltip()
  return

$(document).on('turbolinks:load', enable_tooltips )