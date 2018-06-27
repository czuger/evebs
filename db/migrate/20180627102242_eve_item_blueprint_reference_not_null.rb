class EveItemBlueprintReferenceNotNull < ActiveRecord::Migration[5.2]
  def change
    change_column :eve_items, :blueprint_id, :bigint, null: false
  end
end
