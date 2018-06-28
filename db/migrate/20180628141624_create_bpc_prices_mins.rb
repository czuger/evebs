class CreateBpcPricesMins < ActiveRecord::Migration[5.2]
  def change
    create_table :bpc_prices_mins do |t|
      t.references :trade_hub, foreign_key: true, null: false
      t.references :blueprint_component, foreign_key: true, null: false
      t.bigint :volume
      t.float :price, null: false

      t.timestamps
    end
  end
end
