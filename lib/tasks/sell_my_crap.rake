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
          prices_for_item[ min_price ] = order.trade_hub.name if order
        end

        best_price = prices_for_item.keys.min
        trade_hub_name = prices_for_item[ best_price ]

        locations[trade_hub_name] ||= []
        locations[trade_hub_name] << [ item.name, best_price ]
      end
    end

    pp locations

    # items = assets.assets.select{ |e| e.locationID == "#{location}" if e.respond_to?( 'locationID' ) }

    # results = []
    # items.each do |item|
    #   i = EveItem.find_by_cpp_eve_item_id( item.typeID.to_i )
    #   if i
    #     prices = i.prices_advices.where.not( vol_month: nil ).
    #       order( '( min_price * least( vol_month/5, full_batch_size ) ) DESC NULLS LAST' )
    #     # puts prices.to_sql
    #     price = prices.first
    #     if price
    #       results_for_item = [ "#{i.name} - (#{i.id})", "#{price.trade_hub.name} - (#{price.trade_hub_id})",
    #                            price.vol_month.round( 0 ), price.min_price.round( 2 )]
    #       results_for_item << ( price.min_price - price.single_unit_cost ).round( 2 )
    #       results << results_for_item
    #     else
    #       puts "Nothing for #{i.name}"
    #     end
    #   end
    # end
    # results.sort_by!{ |e| e[1] }
    # results.each do |results_for_item|
    #   padded_str = ( '%-50s'*2 + '%25s'*3 ) % results_for_item
    #   puts padded_str
    # end
  end
end