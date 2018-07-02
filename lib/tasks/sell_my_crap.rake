namespace :extra_tools do

  desc "Sell my crap"
  task :sell_my_crap => :environment do

    assets = Esi::DownloadAssets.new( nil ).get_list

    locations = {}
    accepted_trades_hubs = [ 30002187, 30002510, 30002659, 30000142 ]

    assets.each do |asset|

      # we check if the asset is a component
      item = BlueprintComponent.find_by_cpp_eve_item_id( asset['type_id'])
      item = EveItem.find_by_cpp_eve_item_id( asset['type_id']) unless item

      if item
        prices_for_item = {}
        accepted_trades_hubs.each do |trade_hub_cpp_id|
          min_price = order = nil
          if item.is_a? BlueprintComponentSalesOrder
            min_price = BlueprintComponentSalesOrder.joins( :trade_hub ).where( blueprint_component_id: item.id, 'trade_hubs.eve_system_id': trade_hub_cpp_id ).minimum( :price )
            order = BlueprintComponentSalesOrder.joins( :trade_hub ).where( blueprint_component_id: item.id, 'trade_hubs.eve_system_id': trade_hub_cpp_id,  price: min_price ).first
          else
            min_price = SalesOrder.joins( :trade_hub ).where( eve_item_id: item.id, 'trade_hubs.eve_system_id': trade_hub_cpp_id ).minimum( :price )
            order = SalesOrder.joins( :trade_hub ).where( eve_item_id: item.id, 'trade_hubs.eve_system_id': trade_hub_cpp_id,  price: min_price ).first
          end
          prices_for_item[ min_price ] = order.trade_hub.name if order && min_price
        end

        best_price = prices_for_item.keys.min
        trade_hub_name = prices_for_item[ best_price ]

        locations[trade_hub_name] ||= []
        locations[trade_hub_name] << [ item.name, best_price ]
      end
    end

    locations.each do |l|
      l[1].each do |pricing|
        puts ( "%-15s %-50s %10.2f" % [l[0], pricing[0], pricing[1]] ) if pricing[1]
      end
    end
  end
end