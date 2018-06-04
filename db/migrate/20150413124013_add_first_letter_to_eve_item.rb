class AddFirstLetterToEveItem < ActiveRecord::Migration[4.2]
  def change
    add_column :eve_items, :first_letter, :string
    add_index :eve_items, :first_letter
  end
end
