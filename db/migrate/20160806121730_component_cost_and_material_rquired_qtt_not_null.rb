class ComponentCostAndMaterialRquiredQttNotNull < ActiveRecord::Migration[4.2]
  def change
    change_column_null :materials, :required_qtt, false
  end
end
