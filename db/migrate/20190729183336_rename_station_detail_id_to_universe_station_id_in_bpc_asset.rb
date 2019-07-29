class RenameStationDetailIdToUniverseStationIdInBpcAsset < ActiveRecord::Migration[5.2]
  def change
    rename_column :bpc_assets, :station_detail_id, :universe_station_id
  end
end
