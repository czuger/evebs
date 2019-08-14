class AddVolumeHistoryColumnsToTradeVolumeEstimation < ActiveRecord::Migration[5.2]
  def change
    add_column :trade_volume_estimations, :region_volume_downloaded, :bigint
    add_column :trade_volume_estimations, :trade_hub_final_estimated_volume, :bigint
  end
end
