class CreateEveMarketVolumes < ActiveRecord::Migration[5.2]
  def change
    create_table :eve_market_volumes do |t|
      t.references :region, foreign_key: true, null: false
      t.references :eve_item, foreign_key: true, null: false
      t.bigint :volume, null: false

      t.timestamps
    end
  end
end
