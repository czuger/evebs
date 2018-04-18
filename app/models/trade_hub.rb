class TradeHub < ApplicationRecord

  has_many :min_prices
  belongs_to :region
  has_many :crest_prices_last_month_averages, through: :region, source: :trade_hubs

  def get_selling_eve_items_ids( user )
    TradeOrder.where( user_id: user.id, trade_hub_id: id ).pluck( :eve_item_id )
  end

end
