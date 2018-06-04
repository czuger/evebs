# This migration comes from caddie (originally 20160707153021)
class CreateCaddieCrestPriceHistoryUpdateLogs < ActiveRecord::Migration[4.2]
  def change
    create_table :caddie_crest_price_history_update_logs do |t|
      t.date :feed_date
      t.integer :update_planning_time
      t.integer :feeding_time

      t.timestamps null: false
    end
    add_index :caddie_crest_price_history_update_logs, :feed_date, unique: true
  end
end
