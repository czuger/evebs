class AddFkToUserSaleOrder < ActiveRecord::Migration[5.2]
  def change
    drop_view :user_sale_order_details
    add_foreign_key :user_sale_orders, :users
    add_foreign_key :user_sale_orders, :eve_items
    add_foreign_key :user_sale_orders, :trade_hubs
    change_column :user_sale_orders, :created_at, :timestamp, null: false
    change_column :user_sale_orders, :updated_at, :timestamp, null: false
    change_column :user_sale_orders, :price, :float, null: false
  end
end
