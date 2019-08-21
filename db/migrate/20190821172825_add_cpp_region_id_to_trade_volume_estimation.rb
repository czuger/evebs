class AddCppRegionIdToTradeVolumeEstimation < ActiveRecord::Migration[5.2]
  def change
    TradeVolumeEstimation.delete_all

    add_column :trade_volume_estimations, :cpp_region_id, :integer

    change_column :trade_volume_estimations, :region_volume_total, :bigint, null: true, default: nil
    change_column :trade_volume_estimations, :percentage, :float, null: true, default: nil

    rename_column :trade_volume_estimations, :volume_total, :trade_hub_volume_computed_from_orders
    rename_column :trade_volume_estimations, :region_volume_total, :region_volume_computed_from_orders
    rename_column :trade_volume_estimations, :percentage, :trade_hub_to_region_percentage_computed_from_orders
    rename_column :trade_volume_estimations, :region_volume_downloaded, :region_volume_downloaded_from_history

    rename_column :trade_volume_estimations, :trade_hub_final_estimated_volume, :trade_hub_volume_adjusted_from_percentage

    remove_column :trade_volume_estimations, :eve_item_id
    remove_column :trade_volume_estimations, :universe_system_id

    add_column :trade_volume_estimations, :cpp_type_id, :integer, null: false
    add_column :trade_volume_estimations, :cpp_system_id, :integer, null: false

    add_index :trade_volume_estimations, [ :cpp_type_id, :cpp_system_id ], unique: true
    add_index :trade_volume_estimations, :cpp_region_id
  end
end
