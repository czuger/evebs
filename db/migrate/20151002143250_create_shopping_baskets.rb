class CreateShoppingBaskets < ActiveRecord::Migration[4.2]
  def change
    create_table :shopping_baskets do |t|
      t.references :user, index: true, foreign_key: true, null: false
      t.references :trade_hub, index: true, foreign_key: true, null: false
      t.references :eve_item, index: true, foreign_key: true, null: false

      t.timestamps null: false
    end
  end
end
