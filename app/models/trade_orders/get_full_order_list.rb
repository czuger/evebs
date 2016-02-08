module TradeOrders::GetFullOrderList

  private

  # Get the full order list for one
  def get_full_order_list( full_orders_list )

    full_orders_list.each do |order|
      puts "Order received #{order.typeID}, #{order.stationID}, #{order.price}"
      eve_item_id = EveItem.to_eve_item_id(order.typeID.to_i)
      trade_hub_id =  Station.to_trade_hub_id(order.stationID.to_i)
      if trade_hub_id && eve_item_id
        to = TradeOrder.find_by_user_id_and_eve_item_id_and_trade_hub_id(user.id, eve_item_id, trade_hub_id)
        if to
          # Si l'ordre existe déja on le renouvelle
          puts "Found #{to.inspect}, updating"
          to.update_attributes( { new_order: true, price: order.price } )
        else
          # Sinon on en cree un
          puts "Order not found - creating a new one"
          TradeOrder.create!( user: user, eve_item_id: eve_item_id, trade_hub_id: trade_hub_id, new_order: true, price: order.price )
        end
      else
        STDERR.puts "#{Time.now} - TradeOrder.get_trade_orders - Unable to find eve item for id #{order.typeID}" unless eve_item_id
        STDERR.puts "#{Time.now} - TradeOrder.get_trade_orders - Unable to find trade hub for station #{order.stationID}" unless trade_hub_id
      end
    end

  end
end