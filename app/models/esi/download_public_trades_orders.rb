class Esi::DownloadPublicTradesOrders < Esi::Download

  def download

    Misc::Banner.p 'About to download sales and buy orders'

    trade_hubs_ids = TradeHub.pluck( :eve_system_id ).to_set
    eve_items_ids = EveItem.pluck( :cpp_eve_item_id ).to_set

    @systems_to_name = Hash[ UniverseSystem.pluck( :cpp_system_id, :name ) ]

    regions_data = {}
    rejected_orders_by_trade_hub = {}
    rejected_orders_by_type = {}

    File.open('data/public_trades_orders.json_stream', 'w') do |f|

      Region.all.each do |region|

        if @verbose_output
          puts "About to download orders for #{region.name}"
        end

        @rest_url = "markets/#{region.cpp_region_id}/orders/"
        orders_data = get_all_pages

        if @verbose_output
          puts "#{orders_data.count} orders to process in #{region.name}"
        end

        regions_data[region.id] = { orders_to_process: orders_data.count, final_orders_count: 0 }

        orders_data_hash = {}

        # Filter orders with same order_id in the region
        orders_data.each do |order_data|

          if orders_data_hash[order_data['order_id']]
            puts "Found duplicate order for #{order_data['order_id']}"
          else
            orders_data_hash[order_data['order_id']] = order_data
          end
        end

        orders_data_hash.values.each do |order_data|

          unless trade_hubs_ids.include?( order_localisation_key( order_data ) )
            rejected_orders_by_trade_hub[ order_localisation_key( order_data ) ] ||= 0
            rejected_orders_by_trade_hub[ order_localisation_key( order_data ) ]  += 1
            next
          end

          unless eve_items_ids.include?( order_data['type_id'] )
            rejected_orders_by_type[ order_data['type_id'] ] ||= 0
            rejected_orders_by_type[ order_data['type_id'] ]  += 1
            next
          end

          if order_data['volume_remain'] == 0
            puts "volume_remain = 0 found for order #{order_data['order_id']}."
            next
          end

          order = { duration: order_data['duration'], is_buy_order: order_data['is_buy_order'], issued: order_data['issued'],
                      min_volume: order_data['min_volume'], order_id: order_data['order_id'], price: order_data['price'],
                      range: order_data['range'], system_id: order_data['system_id'], type_id: order_data['type_id'],
                      volume_remain: order_data['volume_remain'], volume_total: order_data['volume_total'] }

          regions_data[region.id][:final_orders_count] += 1

          f.puts( order.to_json )

        end
      end
    end

    File.open('data/regions_data.yaml', 'w') { |f| f.write regions_data.to_yaml }

    File.open('log/rejected_orders_by_trade_hub.txt','w') do |f|
      rejected_orders_by_trade_hub = rejected_orders_by_trade_hub.map{ |e| [ e[1], e[0] ] }.sort.reverse
      PP.pp(rejected_orders_by_trade_hub,f )
    end

    File.open('log/rejected_orders_by_type.txt','w') do |f|
      rejected_orders_by_type = rejected_orders_by_type.map{ |e| [ e[1], e[0] ] }.sort.reverse
      PP.pp(rejected_orders_by_type,f )
    end

  end

  private

  def order_localisation_key( order_data )
    system_name = @systems_to_name[ order_data['system_id'].to_i ]
    system_name ||= order_data['system_id']

    "#{system_name} : #{order_data['location_id']}"
  end

end