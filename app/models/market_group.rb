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
    File.open( 'tmp/items_tree.rb', 'w' ) do |file|
      arr = []
      items_hash = {}
      self.roots.each do |children|
        next if EVE_ITEM_NOT_SHOWED_GROUPS.include?( children.id )
        arr << build_items_tree_sub( children, items_hash )
      end

      file.puts( '$items_hash=' )
      PP.pp( items_hash, file )
      file.puts( ';' )
      file.puts

      file.puts( '$items_tree=' )
      PP.pp( arr, file )
      file.puts( ';' )
      file.puts
    end

    File.open( 'tmp/items_tree.rb', 'r' ) do |file|
      File.open( 'app/models/items_tree.rb', 'w' ) do |final_file|
        file.each_line do |line|
          line = line.gsub( /"ITEM_HASH_(\d+)"/, '$items_hash[ \1 ]' )
          final_file.puts( line )
        end
      end
    end

  end

  def self.build_items_tree_sub( node, items_hash )
    result = { text: "#{node.name}", internal_node_id: node.id, item: false, 'showCheckbox': false }
    if node.leaf?
      # puts node.ancestors.map{ |e| e.name }.join( '-' )
      items = EveItem.where( market_group_id: node.id, involved_in_blueprint: true ).pluck( :name, :id )
                .map{ |e| { text: e[0], internal_node_id: e[1], item: true, 'showCheckbox': true } }
      # pp items
      items.each do |item|
        items_hash[ item[ :internal_node_id ] ] = item
      end

      return false if items.empty?
      result[ :nodes ] = items.map{ |e| "ITEM_HASH_#{e[ :internal_node_id ]}" }
    else
      nodes = []
      node.children.each do |child|
        sub_nodes = build_items_tree_sub( child, items_hash )
        nodes << sub_nodes if sub_nodes
      end
      return false if nodes.empty?
      result[ :nodes ] = nodes
    end
    result
  end

end
