class SalesDaily < ApplicationRecord
  belongs_to :trade_hub
  belongs_to :eve_item

  def self.compute_sold_amounts

    Banner.p 'About to compute SalesDailies'

    orders = SalesOrder.having('count(order_id) > 1').group(:order_id).pluck(:order_id )

    sales_dailies = []

    orders.each do |o|

      sorted_orders = SalesOrder.where(order_id: o ).order('volume DESC' ).to_a

      if sorted_orders.count > 1

        highest_order = sorted_orders.shift

        until sorted_orders.empty?
          lower_order = sorted_orders.shift

          sold_amount = highest_order.volume - lower_order.volume
          sold_price = highest_order.price

          sales_dailies << SalesDaily.new( day: highest_order.day, trade_hub_id: o.trade_hub_id, eve_item_id: o.eve_item_id,
                                           volume: sold_amount, price: sold_price, order_id: highest_order.order_id )

          highest_order = lower_order
        end
      end
    end

    ActiveRecord::Base.transaction do
      SalesDaily.delete_all
      SalesDaily.import!( sales_dailies )
    end

  end

end
