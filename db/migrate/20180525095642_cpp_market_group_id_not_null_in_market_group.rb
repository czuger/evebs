class CppMarketGroupIdNotNullInMarketGroup < ActiveRecord::Migration[5.2]
  def change
    change_column :market_groups, :cpp_market_group_id, :integer, null: false
    change_column :market_groups, :name, :string, null: false
    remove_column :market_groups, :cpp_type_ids
  end
end
