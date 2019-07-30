class RenameUniverseSystemsIdToUniverseSystemIdInUniverseStation < ActiveRecord::Migration[5.2]
  def change
    rename_column :universe_stations, :universe_systems_id, :universe_system_id
  end
end
