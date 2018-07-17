class ConnectUserToBpcAssets < ActiveRecord::Migration[5.2]
  def change
    remove_column :bpc_assets, :character_id

    add_column :bpc_assets, :user_id, :bigint, null: false
    add_foreign_key :bpc_assets, :users
  end
end
