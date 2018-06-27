class CreateBlueprintComponentSalesOrders < ActiveRecord::Migration[5.2]
  def change
    create_table :blueprint_component_sales_orders do |t|
      t.references :trade_hub, foreign_key: true, null: false
      t.references :blueprint_component, foreign_key: true, null: false, index: false

      t.bigint :cpp_order_id, null: false, index: { unique: true }

      t.bigint :volume, null: false
      t.float :price, null: false
      t.boolean :touched, null: false, default: false

      t.timestamps
    end
    add_index :blueprint_component_sales_orders, :blueprint_component_id, name: :index_bcso_blueprint_component
  end
end
