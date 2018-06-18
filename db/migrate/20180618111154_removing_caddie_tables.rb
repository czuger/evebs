class RemovingCaddieTables < ActiveRecord::Migration[5.2]
  def change
    drop_table :caddie_crest_price_history_last_day_timestamps
    drop_table :caddie_crest_price_history_update_logs
    drop_table :caddie_crest_price_history_updates
  end
end
