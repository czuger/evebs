class CreateMinPriceDailies < ActiveRecord::Migration[5.2]
  def change
    create_table :min_price_dailies do |t|

      t.references :eve_item, foreign_key: true, null: false, index: false
      t.references :trade_hub, foreign_key: true, null: false, index: false
      t.date :day, null: false
      t.float :price, null: false

      t.timestamps
    end

    add_index :min_price_dailies, [ :eve_item_id, :trade_hub_id, :day ], unique: true
  end
end
