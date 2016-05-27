# This migration comes from caddie (originally 20160524122651)
class CreateCaddieCrestPriceHistoryUpdates < ActiveRecord::Migration

  def change
    create_table :caddie_crest_price_history_updates do |t|
      t.references :eve_item, foreign_key: true
      t.references :region, foreign_key: true
      t.date :max_update
      t.date :max_eve_item_create
      t.date :max_region_create
      t.date :max_date
      t.integer :nb_days
      t.string :process_queue
      t.integer :process_queue_priority
      t.date :next_process_date

      t.timestamps null: false
    end
    add_index :caddie_crest_price_history_updates, [ :eve_item_id, :region_id ], unique: true, name: :index_caddie_cphu_on_eve_item_id_and_region_id
  end

end
