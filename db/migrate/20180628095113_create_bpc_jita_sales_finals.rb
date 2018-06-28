class CreateBpcJitaSalesFinals < ActiveRecord::Migration[5.2]
  def change
    create_table :bpc_jita_sales_finals do |t|
      t.references :blueprint_component, foreign_key: true
      t.bigint :volume, null: false
      t.float :price, null: false
      t.bigint :cpp_order_id, null: false

      t.timestamps
    end
  end
end
