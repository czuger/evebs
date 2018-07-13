class AddSecurityStatusToStationDetail < ActiveRecord::Migration[5.2]
  def change
    add_column :station_details, :security_status, :float
  end
end
