class CreateMinPricesLogs < ActiveRecord::Migration
  def change
    create_table :min_prices_logs do |t|
      t.string :random_hash
      t.datetime :retrieve_start
      t.datetime :retrieve_end
      t.integer :duration
      t.integer :updated_items_count

      t.timestamps null: false
    end
  end
end
