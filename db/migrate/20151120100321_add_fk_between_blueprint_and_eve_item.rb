class AddFkBetweenBlueprintAndEveItem < ActiveRecord::Migration
  def change
    add_foreign_key :blueprints, :eve_items
  end
end
