class SalesOrder < ApplicationRecord
  belongs_to :trade_hub

  # Unique usage, can be removed later
  def self.make_order_id_unique
    ActiveRecord::Base.transaction do
      SalesOrder.pluck( :order_id ).each do |oi|
        min_vol = SalesOrder.where( order_id: oi ).pluck( :volume ).min
        SalesOrder.where( order_id: oi ).where.not( volume: min_vol ).delete_all
      end
    end
  end
end
