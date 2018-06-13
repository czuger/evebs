class CreatePriceAvgWeeks < ActiveRecord::Migration[5.2]
  def change
    create_table :price_avg_weeks do |t|
      t.references :trade_hub, foreign_key: true, index: false, null: false
      t.references :eve_item, foreign_key: true, index: false, null: false
      t.float :price, null: false

      t.timestamps
    end

    add_index :price_avg_weeks, [ :trade_hub_id, :eve_item_id ], unique: true
    add_index :sale_orders, [ :cpp_system_id, :cpp_type_id ]
  end
end
