class MarketGroup < ActiveRecord::Base

  has_many :eve_items
  acts_as_tree

  OVERCLASSIFICATION = %w( Large Medium Small )

  EVE_ITEM_NOT_SHOWED_GROUPS = [ 1, 1496, 1335, 1314, 1263, 1103, 926, 870, 236, 68 ]

  def get_market_group_breadcrumb
    prefix = ancestors.reverse.map{ |e| e.name }.compact.join( ' > ' )
    prefix << ' > ' << name unless OVERCLASSIFICATION.include?( name )
    prefix
  end

  def self.build_items_tree
    File.open( 'public/items_tree.json', 'w' ) do |file|
      arr = []
      # i = 0
      self.roots.each do |children|
        next if EVE_ITEM_NOT_SHOWED_GROUPS.include?( children.id )
        result = build_items_tree_sub( children )
        arr << build_items_tree_sub( children ) if result
      end
      file.puts( arr.to_json )
      # PP.pp( arr.to_json, file )
      # pp arr
    end
  end

  private

  def self.build_items_tree_sub( node )
    result = { text: "#{node.name}", internal_node_id: node.id, item: false, 'showCheckbox': false }
    if node.leaf?
      # puts node.ancestors.map{ |e| e.name }.join( '-' )
      items = EveItem.where( market_group_id: node.id, involved_in_blueprint: true ).pluck( :name, :id )
                .map{ |e| { text: e[0], internal_node_id: e[1], item: true, 'showCheckbox': true } }

      return false if items.empty?
      result[ :nodes ] = items
    else
      nodes = []
      node.children.each do |child|
        sub_nodes = build_items_tree_sub( child )
        nodes << sub_nodes if sub_nodes
      end
      return false if nodes.empty?
      result[ :nodes ] = nodes
    end
    result
  end

end
