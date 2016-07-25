# This migration comes from caddie (originally 20160725091214)
class AddIndexesToCrestPriceHistoryUpdate < ActiveRecord::Migration
  def change
    add_index :caddie_crest_price_history_updates, :nb_days
    add_index :caddie_crest_price_history_updates, :process_queue
    add_index :caddie_crest_price_history_updates, :next_process_date
    add_index :caddie_crest_price_history_updates, :thread_slice_id
  end
end
