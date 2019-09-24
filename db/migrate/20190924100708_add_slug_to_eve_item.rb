class AddSlugToEveItem < ActiveRecord::Migration[5.2]
  def change
    add_column :eve_items, :slug, :string
    add_index :eve_items, :slug, unique: true
  end
end
