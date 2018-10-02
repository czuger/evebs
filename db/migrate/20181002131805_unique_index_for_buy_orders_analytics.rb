class UniqueIndexForBuyOrdersAnalytics < ActiveRecord::Migration[5.2]
  def change
    remove_index :buy_orders_analytics, [:trade_hub_id, :eve_item_id]
    add_index :buy_orders_analytics, [:eve_item_id, :trade_hub_id], unique: true

    PricesAdvice.delete_all
    remove_index :prices_advices, :eve_item_id
    remove_index :prices_advices, :trade_hub_id
    add_index :prices_advices, [:eve_item_id, :trade_hub_id], unique: true
  end
end
