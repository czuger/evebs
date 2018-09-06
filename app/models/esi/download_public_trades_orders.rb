class Esi::DownloadPublicTradesOrders < Esi::Download

  def download

    Banner.p 'About to download sales and buy orders'

    trade_hubs_ids = TradeHub.pluck( :eve_system_id ).to_set
    eve_items_ids = EveItem.pluck( :cpp_eve_item_id ).to_set

    orders = []

    File.open('data/public_trades_orders.json_stream', 'w') do |f|

      Region.all.each do |region|

        if @verbose_output
          puts "About to process region : #{region.name}"
        end

        @rest_url = "markets/#{region.cpp_region_id}/orders/"
        orders_data = get_all_pages

        orders_data.each do |order_data|
          next unless trade_hubs_ids.include?( order_data['system_id'] ) && eve_items_ids.include?( order_data['type_id'] )

          order = { duration: order_data['duration'], is_buy_order: order_data['is_buy_order'], issued: order_data['issued'],
                      min_volume: order_data['min_volume'], order_id: order_data['order_id'], price: order_data['price'],
                      range: order_data['range'], system_id: order_data['system_id'], type_id: order_data['type_id'],
                      volume_remain: order_data['volume_remain'], volume_total: order_data['volume_total'] }

          f.puts( order.to_json )

        end
      end
    end
  end
end