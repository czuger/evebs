class AddDownloadHistoryColumnsToRegion < ActiveRecord::Migration[5.2]
  def change
    add_column :universe_regions, :market_items, :jsonb, null: false, default: []
    add_column :universe_regions, :market_items_count, :integer, null: false, default: 0
    add_column :universe_regions, :download_process_id, :integer, null: false, default: 1, limit: 1
  end
end
