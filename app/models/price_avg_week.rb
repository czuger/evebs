class PriceAvgWeek < ApplicationRecord
  belongs_to :trade_hub
  belongs_to :eve_item

  def compute_sold_amounts

    orders = SaleOrder.pluck( :order_id )

    orders.each do |o|

      highest_order = SaleOrder.where( order_id: o ).order( 'volume DESC' ).first

      next_order = SaleOrder.where( order_id: o ).where( 'volume < ?', highest_order.volume ).order( 'volume DESC' ).first

      while next_order
        sold_amount = highest_order.volume - next_order.volume
        sold_price = highest_order.price

        # TODO : save this in a table

        highest_order = next_order
        next_order = SaleOrder.where( order_id: o ).where( 'volume < ?', highest_order.volume ).order( 'volume DESC' ).first
      end
    end
  end
end
