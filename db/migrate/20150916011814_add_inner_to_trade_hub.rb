class AddInnerToTradeHub < ActiveRecord::Migration[4.2]
  def change
    add_column :trade_hubs, :inner, :boolean, default: false
  end
end
