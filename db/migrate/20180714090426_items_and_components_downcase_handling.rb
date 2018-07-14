class ItemsAndComponentsDowncaseHandling < ActiveRecord::Migration[5.2]
  def change
    remove_column :eve_items, :name_lowcase
    add_index :eve_items, 'lower(name)', unique: true
    add_index :blueprint_components, 'lower(name)', unique: true
  end
end
