class AddVolumeToPricesMin < ActiveRecord::Migration[5.2]
  def change
    add_column :prices_mins, :volume, :bigint
    remove_index :prices_mins, :eve_item_id
    remove_index :prices_mins, :trade_hub_id
    add_index :prices_mins, [:eve_item_id, :trade_hub_id], unique: true
  end
end
