class AddIndexOnCppSystemToUniverseSystem < ActiveRecord::Migration[5.2]
  def change
    add_index :universe_systems, :cpp_system_id, unique: true
  end
end
