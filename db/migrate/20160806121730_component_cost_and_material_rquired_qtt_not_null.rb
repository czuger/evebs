class ComponentCostAndMaterialRquiredQttNotNull < ActiveRecord::Migration
  def change
    change_column_null :components, :cost, false
    change_column_null :materials, :required_qtt, false
  end
end
