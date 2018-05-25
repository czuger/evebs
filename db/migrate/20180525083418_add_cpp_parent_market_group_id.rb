class AddCppParentMarketGroupId < ActiveRecord::Migration[5.2]
  def change
    remove_column :market_groups, :cpp_market_group_id
    add_column :market_groups, :cpp_market_group_id, :integer
    add_column :market_groups, :cpp_parent_market_group_id, :integer
  end
end
