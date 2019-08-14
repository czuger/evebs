class CppStarIdNotNullInUniverseSystem < ActiveRecord::Migration[5.2]
  def change
    change_column :universe_systems, :cpp_star_id, :integer, null: true
  end
end
