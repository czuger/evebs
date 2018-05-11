class SetMarketGroupIdNullableToEveItem < ActiveRecord::Migration[5.2]
  def change
    change_column :eve_items, :market_group_id, :integer, null: true
  end
end
