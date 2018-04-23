class CreateEveMarketsPrices < ActiveRecord::Migration[5.2]
  def change
    create_table :eve_markets_prices do |t|
      t.integer :type_id, null: false, index: {unique: true}
      t.float :average_price
      t.float :adjusted_price, null: false

      t.timestamps
    end
  end
end
