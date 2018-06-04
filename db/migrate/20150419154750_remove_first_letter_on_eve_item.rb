class RemoveFirstLetterOnEveItem < ActiveRecord::Migration[4.2]
  def change
    remove_column :eve_items, :first_letter, :string
  end
end
