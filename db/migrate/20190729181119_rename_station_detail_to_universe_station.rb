class RenameStationDetailToUniverseStation < ActiveRecord::Migration[5.2]
  def change
    rename_table :station_details, :universe_stations
  end
end
