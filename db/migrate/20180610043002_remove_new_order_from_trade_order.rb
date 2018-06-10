class RemoveNewOrderFromTradeOrder < ActiveRecord::Migration[5.2]
  def change
    remove_column :trade_orders, :new_order, :boolean
    change_column :trade_orders, :user_id, :integer, null: false
    change_column :trade_orders, :eve_item_id, :integer, null: false
    change_column :trade_orders, :trade_hub_id, :integer, null: false
  end
end
