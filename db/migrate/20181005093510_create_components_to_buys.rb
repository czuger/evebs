class CreateComponentsToBuys < ActiveRecord::Migration[5.2]
  def change
    create_table :components_to_buys do |t|
      t.references :user, foreign_key: true, null: false
      t.references :eve_item, foreign_key: true, null: false
      t.integer :quantity, null: false

      t.timestamps
    end
  end

end
