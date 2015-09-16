class CreateMarketGroups < ActiveRecord::Migration
  def change
    create_table :market_groups do |t|

      t.string :cpp_market_group_id, null: false
      t.string :name, null: false

      t.integer :parent_id

      t.timestamps null: false
    end
    add_index :market_groups, :cpp_market_group_id, unique: true
  end
end
