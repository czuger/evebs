class TradeHub < ActiveRecord::Base
  has_many :min_prices
  belongs_to :region

  def self.get_selling_eve_items_ids( user )
    TradeOrder.where( user_id: user.id, trade_hub_id: id ).pluck( :eve_item_id )
  end

end
