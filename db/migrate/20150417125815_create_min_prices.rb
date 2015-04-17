class CreateMinPrices < ActiveRecord::Migration
  def change
    create_table :min_prices do |t|
      t.references :eve_item, index: true
      t.references :trade_hub, index: true
      t.float :min_price

      t.timestamps
    end
  end
end
