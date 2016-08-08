class ComponentCostAndMaterialRquiredQttNotNull < ActiveRecord::Migration
  def change
    change_column_null :materials, :required_qtt, false
  end
end
