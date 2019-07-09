class AddFkToUserSaleOrder < ActiveRecord::Migration[5.2]
  def change
    drop_view :user_sale_order_details
    add_foreign_key :user_sales_orders, :users
    add_foreign_key :user_sales_orders, :eve_items
    add_foreign_key :user_sales_orders, :trade_hubs
    change_column :user_sales_orders, :created_at, :timestamp, null: false
    change_column :user_sales_orders, :updated_at, :timestamp, null: false
    change_column :user_sales_orders, :price, :float, null: false
  end
end
