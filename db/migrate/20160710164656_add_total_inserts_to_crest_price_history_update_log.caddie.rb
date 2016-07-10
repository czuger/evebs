# This migration comes from caddie (originally 20160710163612)
class AddTotalInsertsToCrestPriceHistoryUpdateLog < ActiveRecord::Migration
  def change
    add_column :caddie_crest_price_history_update_logs, :total_inserts, :integer
  end
end
