class CreateSaleOrders < ActiveRecord::Migration[5.2]
  def change
    create_table :sale_orders do |t|
      t.date :day, null: false
      t.integer :cpp_system_id, null: false
      t.integer :cpp_type_id, null: false
      t.bigint :volume, null: false
      t.float :price, null: false
      t.bigint :order_id, null: false, index: { unique: true }

      t.timestamps
    end
  end
end
