root = exports ? this

original_items_tree = null
filtered_items_tree = null
tree = null

deep_filter = ( elements_array ) ->

  empty = true
  filtered_array = []

  for element in elements_array

    sub_list = []
    sub_array_empty = true

    if element.nodes
      [ sub_list, sub_array_empty ] = deep_filter( element.nodes )

      unless sub_array_empty
        empty = false
        element.nodes = sub_list
        filtered_array.push( element )
      else
        match_string = "#{$('#filter').val().toLowerCase()}"
        if element.text.toLowerCase().match( match_string ) != null
          empty = false
#          element.nodes = sub_list
          filtered_array.push( element )

    else
      match_string = "#{$('#filter').val().toLowerCase()}"
      match = element.text.toLowerCase().match( match_string )
      if match != null
        empty = false
        filtered_array.push( element )
#        console.log( 'kept', element.text, match_string, match, )
      else
#        console.log( 'rejected', element.text, match_string, match, )

#  console.log( filtered_array )
  [ filtered_array, empty ]


setFilter = ->
  $('#filter').keyup( ->
    f = JSON.parse( original_items_tree )
    [ f, _ ] = deep_filter( f )
    filtered_items_tree = JSON.stringify(f)

    tree = $('#tree').treeview data: filtered_items_tree, levels: 0, showCheckbox: true
  )


selectItem = ( node, check_state ) ->
  $.post '/choose_items/select_items', { id: node.internal_node_id, item: node.item, check_state: check_state }


getTree = ->

  original_items_tree = $('#items_tree').val()
  filtered_items_tree = original_items_tree

  tree = $('#tree').treeview data: filtered_items_tree, levels: 0, showCheckbox: true
  root.item_ids = JSON.parse( $( '#item_ids' ).val() )

  tree.on 'nodeChecked ', (ev, node) ->
    unless root.checking_items
      selectItem( node, true )
      root.item_ids.push( node.internal_node_id )

  .on 'nodeUnchecked ', (ev, node) ->
    unless root.checking_items
      selectItem( node, false )
      i = 0
      for item_id in root.item_ids
        if node.internal_node_id == item_id
          delete root.item_ids[ i ]
          break
        i += 1

  .on 'nodeExpanded ', (ev, node) ->
    root.checking_items = true
    for children in node.nodes
      children_id = children.internal_node_id
      for item_id in root.item_ids

        if children_id == item_id
          if children.checked
            $('#tree').treeview('uncheckNode', [ children.nodeId, { silent: false } ] )
          else
            $('#tree').treeview('checkNode', [ children.nodeId, { silent: false } ] )
          break

    root.checking_items = false

$(document).on('turbolinks:load'
  ->
    if window.location.pathname == '/choose_items/edit'
      getTree()
      setFilter()
)