class ColumnsNotNullInMaterials < ActiveRecord::Migration[5.2]
  def change
    change_column :materials, :blueprint_id, :integer, null: false
    change_column :materials, :component_id, :integer, null: false
    change_column :materials, :required_qtt, :integer, null: false
  end
end
