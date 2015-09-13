class AddRegionToTradeHub < ActiveRecord::Migration
  def change
    add_reference :trade_hubs, :region, index: true, foreign_key: true
  end
end
