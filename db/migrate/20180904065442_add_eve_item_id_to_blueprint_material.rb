class AddEveItemIdToBlueprintMaterial < ActiveRecord::Migration[5.2]
  def change

    add_reference :blueprint_materials, :eve_items, null: false, foreign_key: true
    add_reference :bpc_assets, :eve_items, null: false, foreign_key: true

  end
end
