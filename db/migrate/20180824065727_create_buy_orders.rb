class CreateBuyOrders < ActiveRecord::Migration[5.2]
  def change
    create_table :buy_orders do |t|
      t.references :trade_hub, foreign_key: true, null: false
      t.references :eve_item, foreign_key: true, null: false
      t.bigint :volume_remain, null: false
      t.float :price, null: false
      t.timestamp :end_time, null: false
      t.boolean :touched, null: false, default: false
      t.bigint :order_id, null: false

      t.timestamps
    end
  end
end
