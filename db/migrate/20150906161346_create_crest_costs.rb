class CreateCrestCosts < ActiveRecord::Migration
  def change
    create_table :crest_costs do |t|
      t.integer :cpp_item_id, null: false
      t.references :eve_item, null: false
      t.float :adjusted_price
      t.float :average_price
      t.float :cost

      t.timestamps
    end
    add_index :crest_costs, :eve_item_id, unique: true
    add_index :crest_costs, :cpp_item_id, unique: true
    add_foreign_key :crest_costs, :eve_items
  end
end
