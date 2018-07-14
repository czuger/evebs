class AddDownloadAssetsVariablesToCharacter < ActiveRecord::Migration[5.2]
  def change
    add_column :characters, :download_assets_running, :boolean, null: false, default: false
    add_column :characters, :last_assets_download, :datetime
  end
end
