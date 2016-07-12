enable_tooltyps = ->
  $('[data-toggle="tooltip"]').tooltip()
  return

$(document).on('turbolinks:load', enable_tooltyps )