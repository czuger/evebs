class RenameStationDetailIdToUniverseStationIdInBpcAssetsStation < ActiveRecord::Migration[5.2]
  def change
    rename_column :bpc_assets_stations, :station_detail_id, :universe_station_id
  end
end
