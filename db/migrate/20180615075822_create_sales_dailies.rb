class CreateSalesDailies < ActiveRecord::Migration[5.2]
  def change
    create_table :sales_dailies do |t|
      t.date :day, null: false
      t.references :trade_hub, foreign_key: true, null: false
      t.references :eve_item, foreign_key: true, null: false
      t.bigint :volume, null: false
      t.float :price, null: false
      t.bigint :order_id, null: false

      t.timestamps
    end
  end
end
