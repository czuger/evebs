class AddCppTypeIdsToMarketGroups < ActiveRecord::Migration[5.2]
  def change
    add_column :market_groups, :cpp_type_ids, :string
  end
end
