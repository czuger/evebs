class RemoveFirstLetterOnEveItem < ActiveRecord::Migration
  def change
    remove_column :eve_items, :first_letter, :string
  end
end
