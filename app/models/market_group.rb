class MarketGroup < ApplicationRecord

  has_many :eve_items
  serialize :cpp_type_ids
  acts_as_tree

  def self.build_items_tree
    File.open( 'data/tmp_items_tree.json', 'w' ) do |file|
      arr = []
      # i = 0
      self.roots.each do |children|
        result = build_items_tree_sub( children )
        arr << build_items_tree_sub( children ) if result
      end
      file.puts( arr.to_json )
      # PP.pp( arr.to_json, file )
      # pp arr
    end
    FileUtils.mv 'data/tmp_items_tree.json', 'data/items_tree.json'
  end

  private

  # TODO : faire un hash avec tous les eve_item_ids dans blueprint, exclure tous les items qui n'ont pas de blueprint
  # Puis trouver un moyen de supprimer les branches vides (mais je crois que c'est fait)

  def self.build_items_tree_sub( node )
    result = { text: "#{node.name}", internal_node_id: node.id, item: false, 'showCheckbox': false }
    if node.leaf?
      # puts node.ancestors.map{ |e| e.name }.join( '-' )
      items = EveItem.joins( :blueprint ).where( market_group_id: node.id ).where.not( cost: nil ).order( :name ).pluck( :name, :id )
                .map{ |e| { text: e[0], internal_node_id: e[1], item: true, 'showCheckbox': true } }

      # p items

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
