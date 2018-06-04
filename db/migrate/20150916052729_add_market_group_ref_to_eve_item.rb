class AddMarketGroupRefToEveItem < ActiveRecord::Migration[4.2]
  def change
    add_reference :eve_items, :market_group, index: true, foreign_key: true
    remove_column :eve_items, :cpp_market_group_id
  end
end
