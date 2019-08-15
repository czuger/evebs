module Process

  class Process::UpdatePublicTradesOrders < UpdateBase

    # il faut gérer la disparition de l'ordre. Est ce qu'on s'en fout ?
    # Dans un premier temps oui (oui, on s'en fout), car on ne sait pas
    # si l'ordre a été annulé, timeout ou bien vendu.
    def update

      Misc::Banner.p 'About to update sales orders'

      set_conversion_hash

      @orders_created = 0
      @orders_updated = 0
      @orders_touched = 0
      @orders_deleted = 0
      @orders_over_time = 0

      @sales_finals_created = 0

      @order_batch_inserter = Libs::BatchBuffer.new( 'PublicTradeOrder', :insert )
      @order_batch_marker = Libs::BatchBuffer.new( 'PublicTradeOrder', :touch )

      orders = File.open('data/public_trades_orders.json_stream', 'r')

      PublicTradeOrder.update_all( touched: false )

      process_orders orders

      @order_batch_inserter.flush_buffer
      @order_batch_marker.flush_buffer

      delete_old_sales_orders

      if @verbose_output
        puts "Orders created : #{@orders_created}"
        puts "Orders updated : #{@orders_updated}"
        puts "Orders touched : #{@orders_touched}"
        puts "Orders deleted : #{@orders_deleted}"
        puts "Orders that failed out of time : #{@orders_over_time}"

        puts "Sales final created : #{@sales_finals_created}"
      end

      update_trade_volume_estimations
    end

    def update_trade_volume_estimations
      # TradeVolumeEstimation.connection.truncate('trade_volume_estimations')

      set_conversion_hash

      cpp_system_to_universe_region_id = Hash[ UniverseSystem.includes( { universe_constellation: :universe_region } ).pluck(:cpp_system_id,'universe_regions.id') ]
      
      tve_batch = Libs::BatchBuffer.new( 'TradeVolumeEstimation', :insert )

      estimations = {}

      File.open( 'data/public_trades_orders.json_stream', 'r' ) do |f|
        f.each do |line|
          data = JSON.parse( line )

          next if data['is_buy_order']

          cpp_system_id = data['system_id']
          cpp_type_id = data['type_id']
          region_id = cpp_system_to_universe_region_id[cpp_system_id]

          estimations[cpp_type_id] ||= { systems:{}, regions: {} }

          estimations[cpp_type_id][:systems][cpp_system_id] ||= 0
          estimations[cpp_type_id][:systems][cpp_system_id] += data['volume_total']

          estimations[cpp_type_id][:regions][region_id] ||= 0
          estimations[cpp_type_id][:regions][region_id] += data['volume_total']
        end
      end

      import_buffer = []

      estimations.each_pair do |cpp_type_id, val|
        eve_item_id = @eve_item_conversion_hash[cpp_type_id]

        val[:systems].each_pair do |cpp_system_id, volume|
          universe_system_id = @universe_system_conversion_hash[cpp_system_id]
          universe_region_id = cpp_system_to_universe_region_id[cpp_system_id]

          region_volume = val[:regions][universe_region_id]

          # puts "#{cpp_type_id}, #{universe_system_id} : #{volume}, #{region_volume}, #{volume.to_f/region_volume}"
          import_buffer << TradeVolumeEstimation.new( universe_system_id: universe_system_id,
                                                        eve_item_id: eve_item_id, volume_total: volume,
                                                        region_volume_total: region_volume, percentage: volume.to_f/region_volume )
        end
      end

      TradeVolumeEstimation.import( import_buffer,
                                    on_duplicate_key_update: {conflict_target: [:universe_system_id, :eve_item_id],
                                                              columns: [:volume_total, :region_volume_total, :percentage] } )

      TradeVolumeEstimation.update_all( 'trade_hub_final_estimated_volume = region_volume_downloaded*percentage' )
    end

    private

    def process_orders( orders )

      process_count = 0

      orders.each_line do |json_encoded_order|

        process_count += 1
        # puts "#{process_count} orders processed" if process_count % 10000 == 0

        server_order_data = JSON.parse( json_encoded_order )
        server_order_data.symbolize_keys!

        trade_hub_id = @trade_hub_conversion_hash[ server_order_data[:system_id] ]
        eve_item_id = @eve_item_conversion_hash[ server_order_data[:cpp_type_id] ]

        unless trade_hub_id
          puts "Unable to find a trade hub for #{server_order_data[:system_id]} - @trade_hub_conversion_hash.count = #{@trade_hub_conversion_hash.count}" if @verbose_output
        end

        unless eve_item_id
          puts "Unable to find an eve item for #{server_order_data[:cpp_type_id]} - @@eve_item_conversion_hash.count = #{@eve_item_conversion_hash.count}" if @verbose_output
        end

        trade_order = PublicTradeOrder.find_by_order_id( server_order_data[:order_id] )

        # pp order

        issued = DateTime.parse( server_order_data[:issued] )
        duration = server_order_data[:duration]
        end_time = issued + duration.days

        if trade_order
          # The order already exist
          if trade_order.volume_remain != server_order_data[:volume_remain] || trade_order.end_time != end_time ||
              trade_order.price != server_order_data[:price]
            # And has changed

            # We create a sale order, only for sale orders
            unless server_order_data[:is_buy_order]
              # And only if the volume has changed (not if the price have changed)
              if trade_order.volume_remain != server_order_data[:volume_remain]
                create_sales_final_record( trade_order, server_order_data )
              end
            end

            trade_order.volume_remain = server_order_data[:volume_remain]
            trade_order.end_time = end_time
            trade_order.price = server_order_data[:price]
            trade_order.touched = true
            trade_order.save!

            @orders_updated += 1
          else
            @order_batch_marker.add_data( trade_order.id )
            @orders_touched += 1
          end

        else
          # The trade order does not exist

          @order_batch_inserter.add_data  PublicTradeOrder.new(
              is_buy_order: server_order_data[:is_buy_order], end_time: end_time, min_volume: server_order_data[:min_volume], order_id: server_order_data[:order_id],
              price: server_order_data[:price], range: server_order_data[:range], trade_hub_id: trade_hub_id, eve_item_id: eve_item_id,
              volume_remain: server_order_data[:volume_remain], volume_total: server_order_data[:volume_total], touched: true
          )
          @orders_created += 1
        end
      end
    end

    def create_sales_final_record( old_record_order, new_record_data )
      volume = old_record_order.volume_remain - new_record_data[:volume_remain]
      price = new_record_data[:price]

      SalesFinal.create!(
          day: Time.now, trade_hub_id: old_record_order.trade_hub_id, eve_item_id: old_record_order.eve_item_id, volume: volume,
          price: price, order_id: old_record_order.order_id )

      @sales_finals_created += 1
    end

    def delete_old_sales_orders
      # We assume that all old orders are closed as selling. We will have to estimate the orders that have been manually closed.
      PublicTradeOrder.where( touched: false, is_buy_order: false ).where( 'end_time < ?', Time.now ).each do |old_order|
        tmp_record = { volume_remain: old_order.volume_remain, price: old_order.price }
        create_sales_final_record( old_order, tmp_record )
      end

      @orders_over_time = PublicTradeOrder.where( touched: false ).where( 'end_time >= ?', Time.now ).count

      sales_orders_to_delete = PublicTradeOrder.where( touched: false )
      @orders_deleted = sales_orders_to_delete.count
      sales_orders_to_delete.delete_all
    end

    def set_conversion_hash
      @trade_hub_conversion_hash ||= Hash[ TradeHub.pluck( :eve_system_id, :id ) ]
      @eve_item_conversion_hash ||= Hash[ EveItem.pluck( :cpp_eve_item_id, :id ) ]
      @universe_system_conversion_hash ||= Hash[ UniverseSystem.pluck( :cpp_system_id, :id ) ]
    end

  end
end