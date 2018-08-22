class AddSelectedAssetsStationIdToUser < ActiveRecord::Migration[5.2]
  def change
    add_column :users, :selected_assets_station_id, :bigint
    add_foreign_key :users, :station_details, column: :selected_assets_station_id
  end
end
