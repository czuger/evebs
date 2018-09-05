class RemoveBlueprintComponentStuff < ActiveRecord::Migration[5.2]
  def change
    drop_view :component_to_buys

    BpcAsset.delete_all
    remove_column :bpc_assets, :blueprint_component_id

    drop_table :bpc_prices_mins
    drop_table :bpc_jita_sales_finals
    drop_table :blueprint_component_sales_orders

    BlueprintMaterial.delete_all
    remove_column :blueprint_materials, :blueprint_component_id

    drop_table :blueprint_components

    add_
  end
end
