class CreatePricesAdvices < ActiveRecord::Migration[4.2]
  def change
    create_table :prices_advices do |t|
      t.references :eve_item, index: true, foreign_key: true, null: false
      t.references :trade_hub, index: true, foreign_key: true, null: false
      t.references :region, index: true, foreign_key: true

      t.bigint :vol_month
      t.bigint :vol_day
      t.float :cost
      t.float :min_price
      t.float :avg_price

      t.float :daily_monthly_pcent, limit: 4

      t.integer :full_batch_size
      t.integer :prod_qtt
      t.float :single_unit_cost

      t.timestamps null: false
    end
  end
end
