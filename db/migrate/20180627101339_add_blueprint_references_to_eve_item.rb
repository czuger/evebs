class AddBlueprintReferencesToEveItem < ActiveRecord::Migration[5.2]
  def change
    add_reference :eve_items, :blueprint, foreign_key: true
  end
end
