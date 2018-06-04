class CreateTradeOrders < ActiveRecord::Migration[4.2]
  def change
    create_table :trade_orders do |t|
      t.references :user, index: true
      t.references :eve_item, index: true
      t.references :trade_hub, index: true

      t.timestamps
    end
  end
end
