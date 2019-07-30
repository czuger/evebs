class AddOrdersToTradeVolumeEstimations < ActiveRecord::Migration[5.2]
  def change
    add_column :trade_volume_estimations, :orders, :bigint, array: true, null: false, default: []
  end
end
