require 'set'

module Setup::EveItem

  # This is the right eve item update. It rely on the files downloaded from CPP
  def update_eve_item_list

    new_items = {}

    # import new items
    Spreadsheet.client_encoding = 'UTF-8'
    book = Spreadsheet.open 'work/invTypes.xls'
    sheet = book.worksheet( 0 )
    sheet.each do |row|
      # We take only marketable items and published items
      if row[ 11 ] && row[ 10 ] == 1.0
        id, name, market_group = [ row[ 0 ].to_i, row[ 2 ], row[ 11 ].to_i ]
        new_items[ id ] = { id: id, name: name, market_group: market_group }
      end
    end

    blueprints = Blueprint.load_blueprint_array
    items_involved_in_blueprints = Set.new
    blueprints.each do |e|

      # We skip blueprints for items not in new_items list (excluding non published items)
      next unless new_items.has_key?( e[ :produced_item_id ] )

      # There still are blueprints without materials. So we need dont keep those blueprints
      if e[ :materials ]
        items_involved_in_blueprints << e[ :produced_item_id ]
        items_involved_in_blueprints += e[ :materials ].keys
      end
    end

    new_items.keys.each do |key|
      new_items.delete( key ) unless items_involved_in_blueprints.include?( key )
    end

    current_items_ids = EveItem.pluck( :cpp_eve_item_id )
    # pp current_items_ids

    new_items_ids = new_items.keys - current_items_ids
    to_remove_ids = current_items_ids - new_items.keys

    puts 'New items'
    new_items_ids.each do |id|
      puts new_items[ id ].inspect
    end

    puts 'To remove'
    to_remove_ids.each do |id|
      item = EveItem.find_by_cpp_eve_item_id( id )
      puts "Removing : #{item.inspect}"
      item.destroy
    end

  end
end