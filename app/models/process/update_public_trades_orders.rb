class Process::UpdatePublicTradesOrders

  # il faut gérer la disparition de l'ordre. Est ce qu'on s'en fout ?
  # Dans un premier temps oui (oui, on s'en fout), car on ne sait pas
  # si l'ordre a été annulé, timeout ou bien vendu.
  def update

    Banner.p 'About to update sales orders'

    @trade_hub_conversion_hash = Hash[ TradeHub.pluck( :eve_system_id, :id ) ]
    @eve_item_conversion_hash = Hash[ EveItem.pluck( :cpp_eve_item_id, :id ) ]

    @orders_created = 0
    @orders_updated = 0
    @orders_touched = 0
    @orders_deleted = 0
    @orders_over_time = 0

    @sales_finals_created = 0
    @sales_finals_deleted = 0

    order_batch_inserter = Libs::BatchInsertBuffer.new( 'PublicTradeOrder' )

    orders = File.open('data/public_trades_orders.json_stream', 'r')

    PublicTradeOrder.update_all( touched: false )

    process_count = 0

    orders.each_line do |json_encoded_order|

      process_count += 1
      puts "#{process_count} orders processed" if process_count % 10000 == 0

      order = JSON.parse( json_encoded_order )
      order.symbolize_keys!

      trade_hub_id = @trade_hub_conversion_hash[ order[:system_id] ]
      eve_item_id = @eve_item_conversion_hash[ order[:type_id] ]
      next unless trade_hub_id && eve_item_id

      trade_order = PublicTradeOrder.find_by_order_id( order[:order_id] )

      # pp order

      issued = DateTime.parse( order[:issued] )
      duration = order[:duration]
      end_time = issued + duration.days

      if trade_order
        # The order already exist
        if trade_order.volume_remain != order[:volume_remain] || trade_order.end_time != end_time ||
            trade_order.price != order[:price]
          # And has changed
          trade_order.volume_remain = order[:volume_remain]
          trade_order.end_time = end_time
          trade_order.price = order[:price]

          @orders_updated += 1
        else
          @orders_touched += 1
        end

        trade_order.touched = true
        trade_order.save!
      else
        # The trade order does not exist

        order_batch_inserter.add_data  PublicTradeOrder.new(
            is_buy_order: order[:is_buy_order], end_time: end_time, min_volume: order[:min_volume], order_id: order[:order_id],
            price: order[:price], range: order[:range], trade_hub_id: trade_hub_id, eve_item_id: eve_item_id,
            volume_remain: order[:volume_remain], volume_total: order[:volume_total]
        )
        @orders_created += 1
      end

    end

    order_batch_inserter.flush_buffer

    # unless @silent_output
    #   puts "Sales orders created : #{@sales_orders_created}" unless @silent_output
    #   puts "Sales orders updated : #{@sales_orders_updated}" unless @silent_output
    #   puts "Sales orders deleted : #{@sales_orders_deleted}" unless @silent_output
    #   puts "Sales orders that failed out of time : #{@sales_orders_over_time}" unless @silent_output
    #
    #   puts "Sales final created : #{@sales_finals_created}" unless @silent_output
    #   puts "Sales final deleted : #{sales_finals_deleted}" unless @silent_output
    #
    #   puts "Buy orders created : #{@buy_orders_created}"
    #   puts "Buy orders updated : #{@buy_orders_updated}"
    #   puts "Buy orders touched : #{@buy_orders_touched}"
    #   puts "Buy orders deleted : #{buy_orders_deleted}"
    # end
  end
end