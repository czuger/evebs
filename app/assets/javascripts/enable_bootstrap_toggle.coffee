$(document).on 'ready turbolinks:load', ->
  $('input[type="checkbox"].toggle').bootstrapToggle()
  # assumes the checkboxes have the class "toggle"
  return
