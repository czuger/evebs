class AddMarketGroupShortcutsToEveItem < ActiveRecord::Migration[5.2]
  def change
    add_column :eve_items, :market_group_path, :json, null: false, default: []
    remove_column :eve_items, :additional_information
    add_column :eve_items, :mass, :float
    add_column :eve_items, :packaged_volume, :float
  end
end
