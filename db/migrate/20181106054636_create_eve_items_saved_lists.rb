class CreateEveItemsSavedLists < ActiveRecord::Migration[5.2]
  def change
    create_table :eve_items_saved_lists do |t|
      t.references :user, foreign_key: true, null: false
      t.string :description, null: false
      t.string :saved_ids, null: false

      t.timestamps
    end
  end
end
