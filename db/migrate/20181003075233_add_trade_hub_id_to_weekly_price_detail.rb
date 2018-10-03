class AddTradeHubIdToWeeklyPriceDetail < ActiveRecord::Migration[5.2]
  def change
    WeeklyPriceDetail.delete_all
    add_reference :weekly_price_details, :trade_hub, foreign_key: true, index: false, null: false

    remove_index :weekly_price_details, [:eve_item_id, :day]
    add_index :weekly_price_details, [:eve_item_id, :trade_hub_id, :day], unique: true, name: :wpd_eve_item_id_trade_hub_id_day
  end
end
