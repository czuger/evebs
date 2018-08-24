class CreateBuyOrdersAnalytics < ActiveRecord::Migration[5.2]
  def change
    create_table :buy_orders_analytics do |t|
      t.references :trade_hub, foreign_key: true, index: false, null: false
      t.references :eve_item, foreign_key: true, index: false, null: false

      t.float :approx_max_price
      t.bigint :over_approx_max_price_volume

      t.timestamps
    end

    add_index :buy_orders_analytics, [ :trade_hub_id, :eve_item_id ], unique: true
  end
end
