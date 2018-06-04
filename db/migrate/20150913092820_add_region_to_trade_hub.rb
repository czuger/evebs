class AddRegionToTradeHub < ActiveRecord::Migration[4.2]
  def change
    add_reference :trade_hubs, :region, index: true, foreign_key: true
  end
end
