class CreateWeeklyPriceDetails < ActiveRecord::Migration[5.2]
  def change
    create_table :weekly_price_details do |t|
      t.references :eve_item, foreign_key: true, null: false
      t.date :day, null: false
      t.float :volume, null: false
      t.float :weighted_avg_price, null: false

      t.timestamps
    end

    add_column :eve_items, :weekly_avg_price, :float
  end
end

