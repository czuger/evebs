class Crest::MarketGroups

  extend Crest::CrestBase

  # TODO : there is a bug, create a test case to find it. It for fury missiles, only inferno has a group and not the rest.
  def self.update_market_group
    puts 'About to update market groups'
    fill_market_group_table

    parsed_data = parsed_data = get_parsed_data( 'market/types' )

    parsed_data["items"].each do |item|
      cpp_market_group_id = item['marketGroup']['id']
      cpp_type_id = item['type']['id']
      eve_item = EveItem.find_by_cpp_eve_item_id(cpp_type_id)
      if eve_item
        market_group = MarketGroup.find_by_cpp_market_group_id( cpp_market_group_id )
        market_group.eve_items << eve_item
      end
    end
  end

  def self.fill_market_group_table
    parsed_data = get_parsed_data( 'market/groups' )

    # Feed the table
    parsed_data["items"].each do |item|
      cpp_market_group_id = item['href'].match( /(\d+)/ )[1]
      name = item['name']
      MarketGroup.find_or_create_by!( cpp_market_group_id: cpp_market_group_id ) do |market|
        market.name = name
      end
    end

    # Then link parents and childrens
    parsed_data["items"].each do |item|
      cpp_market_group_id = item['href'].match( /(\d+)/ )[1]
      if item['parentGroup']
        cpp_parent_group_id = item['parentGroup']['href'].match( /(\d+)/ )[1]
        parent = MarketGroup.find_by_cpp_market_group_id( cpp_parent_group_id )
        children = MarketGroup.find_by_cpp_market_group_id( cpp_market_group_id )
        # puts parent.inspect
        parent.children << children
      end
    end

  end


end