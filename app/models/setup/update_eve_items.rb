require 'set'

module Setup::UpdateEveItems

  include Setup::UpdateMarketGroups

  # This is the right eve item update. It rely on the files downloaded from CPP
  def update_eve_items_list

    # First ensure all markets are present
    # update_market_groups

    new_items = {}

    # import new items
    break_on_tests_counter = 0
    Setup::CppSourcesEveItem.where( published: 1 ).where.not( marketGroupId: nil ).each do |item|
      id, name, market_group = [ item.typeID, item.typeName, item.marketGroupID ]
      new_items[ id ] = { id: id, name: name, market_group: market_group }
      break_on_tests_counter += 1
      break if Rails.env=='test' && break_on_tests_counter > 0
    end

    blueprints = Blueprint.get_blueprints_array_from_cpp_sources

    items_involved_in_blueprints = Set.new
    blueprints.each do |e|

      # We skip blueprints for items not in new_items list (excluding non published items)
      next unless new_items.has_key?( e[ :cpp_produced_type_id ] )

      # There still are blueprints without materials. So we need dont keep those blueprints
      if e[ :materials ]
        items_involved_in_blueprints << e[ :cpp_produced_type_id ]
        items_involved_in_blueprints += e[ :cpp_consumed_material_type_ids ]
      end
    end

    new_items.keys.each do |key|
      new_items.delete( key ) unless items_involved_in_blueprints.include?( key )
    end

    current_items_ids = EveItem.pluck( :cpp_eve_item_id )
    # pp current_items_ids

    new_items_ids = new_items.keys - current_items_ids
    to_remove_ids = current_items_ids - new_items.keys

    new_items_ids.each do |id|
      item_to_add = new_items[ id ]
      puts "Adding #{item_to_add.inspect}"
      market_group = MarketGroup.where( cpp_market_group_id: item_to_add[ :market_group ] ).pluck( :id ).first
      EveItem.create!(
        market_group_id: market_group, cpp_eve_item_id: item_to_add[ :id ], name: item_to_add[ :name ],
        name_lowcase: item_to_add[ :name ].downcase, involved_in_blueprint: true )
    end

    puts 'To remove'
    to_remove_ids.each do |id|
      item = EveItem.find_by_cpp_eve_item_id( id )
      puts "Removing : #{item.inspect}"
      item.destroy
    end

  end
end