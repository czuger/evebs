class SetDownloadProcessIdNullable < ActiveRecord::Migration[5.2]
  def change
    change_column :universe_regions, :download_process_id, :integer, null: true, limit: 1
  end
end
