class AddFkBetweenBlueprintAndEveItem < ActiveRecord::Migration[4.2]
  def change
    add_foreign_key :blueprints, :eve_items
  end
end
