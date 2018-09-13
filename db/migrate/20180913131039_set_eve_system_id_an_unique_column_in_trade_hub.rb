class SetEveSystemIdAnUniqueColumnInTradeHub < ActiveRecord::Migration[5.2]
  def change
    add_index :trade_hubs, :eve_system_id, unique: true
  end
end
