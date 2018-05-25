class AddIndexOnCppMarketGroupIdToMarketGroup < ActiveRecord::Migration[5.2]
  def change
    add_index :market_groups, :cpp_market_group_id, unique: true
  end
end
