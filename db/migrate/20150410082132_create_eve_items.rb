class CreateEveItems < ActiveRecord::Migration[4.2]
  def change
    create_table :eve_items do |t|
      t.integer :eve_item_id
      t.string :name

      t.timestamps
    end
    add_index :eve_items, :eve_item_id
  end
end
