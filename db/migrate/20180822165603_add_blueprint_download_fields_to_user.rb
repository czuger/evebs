class AddBlueprintDownloadFieldsToUser < ActiveRecord::Migration[5.2]
  def change

    add_column :users, :download_blueprints_running, :boolean, default: false, null: false
    add_column :users, :last_blueprints_download, :timestamp

  end
end
