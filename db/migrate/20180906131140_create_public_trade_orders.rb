class CreatePublicTradeOrders < ActiveRecord::Migration[5.2]
  def change
    create_table :public_trade_orders do |t|
      t.references :trade_hub, foreign_key: true, null: false
      t.references :eve_item, foreign_key: true, null: false
      t.bigint :order_id, null: false, index: { unique: true }
      t.boolean :is_buy_order, null: false
      t.datetime :end_time, null: false
      t.float :price, null: false
      t.string :range, null: false
      t.bigint :volume_remain, null: false
      t.bigint :volume_total, null: false
      t.bigint :min_volume, null: false
      t.boolean :touched, null: false, default: false

      t.timestamps
    end
  end
end
