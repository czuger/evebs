class RenameTradeOrderToUserSaleOrder < ActiveRecord::Migration[5.2]
  def change
    rename_table :trade_orders, :user_sale_orders
  end
end
