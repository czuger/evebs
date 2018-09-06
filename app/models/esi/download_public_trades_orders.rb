class Esi::DownloadPublicTradesOrders < Esi::Download

  def download

    Banner.p 'About to download sales and buy orders'

    trade_hubs_ids = TradeHub.pluck( :eve_system_id ).to_set
    eve_items_ids = EveItem.pluck( :cpp_eve_item_id ).to_set

    orders_data_hash = {}
    regions_data = {}

    File.open('data/public_trades_orders.json_stream', 'w') do |f|

      Region.all.each do |region|

        @rest_url = "markets/#{region.cpp_region_id}/orders/"
        orders_data = get_all_pages

        if @verbose_output
          puts "#{orders_data.count} orders to process in #{region.name}"
        end

        regions_data[region.id] = { orders_to_process: orders_data.count, final_orders_count: 0 }

        # Filter orders with same order_id in the region
        orders_data.each do |order_data|

          if orders_data_hash[order_data['order_id']]
            puts "Found duplicate order for #{order_data['order_id']}"
          else
            orders_data_hash[order_data['order_id']] = order_data
          end
        end

        orders_data_hash.values.each do |order_data|
          next unless trade_hubs_ids.include?( order_data['system_id'] ) && eve_items_ids.include?( order_data['type_id'] )

          order = { duration: order_data['duration'], is_buy_order: order_data['is_buy_order'], issued: order_data['issued'],
                      min_volume: order_data['min_volume'], order_id: order_data['order_id'], price: order_data['price'],
                      range: order_data['range'], system_id: order_data['system_id'], type_id: order_data['type_id'],
                      volume_remain: order_data['volume_remain'], volume_total: order_data['volume_total'] }

          regions_data[region.id][:final_orders_count] += 1

          f.puts( order.to_json )

        end
      end
    end

    File.open('data/regions_data.yaml', 'w') {|f| f.write regions_data.to_yaml }

  end
end