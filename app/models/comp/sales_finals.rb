class Comp::SalesFinals

  def self.run

    Banner.p 'About to compute sales final'

    orders_ids = SalesOrder.having('count(order_id) > 1').group(:order_id).pluck(:order_id)

    sales_dailies = []
    sales_count = 0

    orders_ids.each do |oid|
      sales_count += 1

      sorted_orders = SalesOrder.where( order_id: oid ).order( 'volume DESC' ).to_a

      if sorted_orders.count > 1

        highest_order = sorted_orders.shift

        until sorted_orders.empty?
          lower_order = sorted_orders.shift

          sold_amount = highest_order.volume - lower_order.volume
          sold_price = highest_order.price

          sales_dailies << SalesFinal.new(day: highest_order.day, trade_hub_id: highest_order.trade_hub_id, eve_item_id: highest_order.eve_item_id,
                                          volume: sold_amount, price: sold_price, order_id: highest_order.order_id )

          highest_order = lower_order
        end
      end
    end

    ActiveRecord::Base.transaction do
      SalesFinal.delete_all
      SalesFinal.import!(sales_dailies )
    end

  end

end