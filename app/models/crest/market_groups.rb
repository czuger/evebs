class Crest::MarketGroups

  extend Crest::CrestBase

  # TODO : there is a bug, create a test case to find it. It for fury missiles, only inferno has a group and not the rest.
  def self.update_market_group
    puts 'About to update market groups'

    fill_market_group_table

    exit

    parsed_data["items"].each do |item|
      puts "#{item.inspect}" if item['type']['name'] =~ /.*Missile.*/
      cpp_market_group_id = item['marketGroup']['id']
      cpp_type_id = item['type']['id']
      eve_item = EveItem.find_by_cpp_eve_item_id(cpp_type_id)
      puts eve_item.inspect if item['type']['name'] =~ /.*Missile.*/
      if eve_item
        puts "About to update #{eve_item.inspect}"
        market_group = MarketGroup.find_by_cpp_market_group_id( cpp_market_group_id )
        if market_group
          market_group.eve_items << eve_item
          puts "#{eve_item.market_group.inspect}"
        end
      end
    end
  end

  def self.fill_market_group_table
    parsed_data = get_parsed_data( 'market/groups' )

    ActiveRecord::Base.transaction do
      # Feed the table
      parsed_data["items"].each do |item|
        cpp_market_group_id = item['href'].match( /(\d+)/ )[1]
        name = item['name']
        puts "Processing market group #{name}"
        market = MarketGroup.find_or_create_by!( cpp_market_group_id: cpp_market_group_id ) do |market|
          market.name = name
        end
        parsed_data_items_list = get_parsed_data( "market/types/?group=https://public-crest.eveonline.com/market/groups/#{cpp_market_group_id}" )
        parsed_data_items_list['items'].each do |item|
          cpp_type_id = item['type']['id']
          # puts "About to process #{item.inspect}"
          eve_item = EveItem.find_by_cpp_eve_item_id(cpp_type_id)
          if eve_item
            # puts "#{eve_item.name} added to #{market.name}"
            market.eve_items << eve_item
          end
        end
      end

      puts "Start linking parent"
      # Then link parents and childrens
      parsed_data["items"].each do |item|
        cpp_market_group_id = item['href'].match( /(\d+)/ )[1]
        if item['parentGroup']
          cpp_parent_group_id = item['parentGroup']['href'].match( /(\d+)/ )[1]
          parent = MarketGroup.find_by_cpp_market_group_id( cpp_parent_group_id )
          children = MarketGroup.find_by_cpp_market_group_id( cpp_market_group_id )
          puts "#{children.name} linked to #{parent.name}"
          # puts parent.inspect
          parent.children << children
        end
      end

    end

  end


end