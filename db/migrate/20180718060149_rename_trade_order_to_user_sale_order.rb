class RenameTradeOrderToUserSaleOrder < ActiveRecord::Migration[5.2]
  def change
    rename_table :trade_orders, :user_sales_orders
  end
end
