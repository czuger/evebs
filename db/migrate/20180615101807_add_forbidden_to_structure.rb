class AddForbiddenToStructure < ActiveRecord::Migration[5.2]
  def change
    add_column :structures, :forbidden, :boolean, null: false, default: true
    add_index :structures, :forbidden
    change_column :structures, :cpp_structure_id, :bigint, null: false
  end
end
