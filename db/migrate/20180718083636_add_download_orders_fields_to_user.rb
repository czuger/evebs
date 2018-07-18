class AddDownloadOrdersFieldsToUser < ActiveRecord::Migration[5.2]
  def change
    add_column :users, :download_orders_running, :boolean, null: false, default: false
    add_column :users, :last_orders_download, :datetime
  end
end
