class AddDownloadMyAssetsToCharacter < ActiveRecord::Migration[5.2]
  def change
    add_column :characters, :download_my_assets, :boolean, null: false, default: false
    rename_column :users, :last_used_character_id, :current_character_id
  end
end
