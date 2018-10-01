# The depth level is used to to compute the cost in the right order.
# The highest level is 0, and it can go as deep as it can.
# You will have to compute the cost of the lowest level first and then go up to 0

module Process

  class BuildJsonMarketTree

    def build
      Misc::Banner.p 'About to build trees'

      File.open( 'data/tmp_items_tree.json', 'w' ) do |file|
        arr = []
        # i = 0
        MarketGroup.roots.each do |children|
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

    def build_items_tree_sub( node )
      result = { text: "#{node.name}", internal_node_id: node.id, item: false, 'showCheckbox': false }
      if node.leaf?
        # puts node.ancestors.map{ |e| e.name }.join( '-' )
        items = EveItem.where( market_group_id: node.id ).where.not( cost: nil ).order( :name ).pluck( :name, :id )
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

end
