class AddInnerToTradeHub < ActiveRecord::Migration
  def change
    add_column :trade_hubs, :inner, :boolean, default: false
  end
end
