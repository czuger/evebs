root = exports ? this

original_items_tree = null
filtered_items_tree = null
tree = null

deep_filter = ( f ) ->
  console.log( "/#{$('#filter').val().toLowerCase()}/" )
  f = f.filter ( name ) -> name.text.toLowerCase().match( "#{$('#filter').val().toLowerCase()}")
  for e in f
    e.node = deep_filter( e.node )
  f

setFilter = ->
  $('#filter').keydown( ->
    f = JSON.parse( original_items_tree )
    f = deep_filter( f )
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