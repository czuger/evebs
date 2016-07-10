# This migration comes from caddie (originally 20160710163641)
class AddCoSecondsToCrestPriceHistoryUpdateLog < ActiveRecord::Migration
  def change
    add_column :caddie_crest_price_history_update_logs, :co_seconds, :float
  end
end
