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

    @order_batch_inserter = Libs::BatchBuffer.new( 'PublicTradeOrder', :insert )
    @order_batch_marker = Libs::BatchBuffer.new( 'PublicTradeOrder', :touch )

    orders = File.open('data/public_trades_orders.json_stream', 'r')

    PublicTradeOrder.update_all( touched: false )

    process_orders orders

    @order_batch_inserter.flush_buffer
    @order_batch_marker.flush_buffer

    delete_old_sales_orders

    unless @silent_output
      puts "Orders created : #{@orders_created}"
      puts "Orders updated : #{@orders_updated}"
      puts "Orders touched : #{@orders_touched}"
      puts "Orders deleted : #{@orders_deleted}"
      puts "Orders that failed out of time : #{@orders_over_time}"

      puts "Sales final created : #{@sales_finals_created}"
    end
  end

  def process_orders( orders )

    process_count = 0

    orders.each_line do |json_encoded_order|

      process_count += 1
      # puts "#{process_count} orders processed" if process_count % 10000 == 0

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

          create_sales_final_record( trade_order, order )

          trade_order.volume_remain = order[:volume_remain]
          trade_order.end_time = end_time
          trade_order.price = order[:price]
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
            is_buy_order: order[:is_buy_order], end_time: end_time, min_volume: order[:min_volume], order_id: order[:order_id],
            price: order[:price], range: order[:range], trade_hub_id: trade_hub_id, eve_item_id: eve_item_id,
            volume_remain: order[:volume_remain], volume_total: order[:volume_total], touched: true
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
    PublicTradeOrder.where( touched: false ).where( 'end_time < ?', Time.now ).each do |old_order|
      tmp_record = { volume_remain: old_order.volume_remain, price: old_order.price }
      create_sales_final_record( old_order, tmp_record )
    end

    @orders_over_time = PublicTradeOrder.where( touched: false ).where( 'end_time >= ?', Time.now ).count

    sales_orders_to_delete = PublicTradeOrder.where( touched: false )
    @orders_deleted = sales_orders_to_delete.count
    sales_orders_to_delete.delete_all
  end

end