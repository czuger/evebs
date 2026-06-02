namespace :extra_tools do

  desc 'Sell my crap'
  task :sell_my_crap => :environment do

    user = User.find_by_name('Gomex')
    locations = {}
    accepted_trades_hubs = [ 30002187, 30002510, 30002659, 30000142 ]

    selected_station_id = user.selected_assets_station_id
    assets = user.bpc_assets.where( station_detail_id: selected_station_id ).includes( :station_detail, :eve_item )

    assets.each do |asset|

      item = asset.eve_item

      prices_for_item = {}
      accepted_trades_hubs.each do |trade_hub_cpp_id|
        min_price = order = nil

        min_price = PublicTradeOrder.joins( :trade_hub ).where(
            eve_item_id: item.id, 'trade_hubs.eve_system_id': trade_hub_cpp_id, is_buy_order: false ).minimum( :price )

        order = PublicTradeOrder.joins( :trade_hub ).where(
            eve_item_id: item.id, 'trade_hubs.eve_system_id': trade_hub_cpp_id,  price: min_price, is_buy_order: false  ).first

        prices_for_item[ min_price ] = order.trade_hub.name if order && min_price
      end

      best_price = prices_for_item.keys.min
      trade_hub_name = prices_for_item[ best_price ]

      locations[trade_hub_name] ||= []
      locations[trade_hub_name] << [ item.name, best_price ]
    end

    locations.each do |l|
      l[1].each do |pricing|
        puts ( '%-15s %-50s %10.2f' % [l[0], pricing[0], pricing[1]] ) if pricing[1]
      end
    end
  end
end