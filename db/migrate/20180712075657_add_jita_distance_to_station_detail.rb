class AddJitaDistanceToStationDetail < ActiveRecord::Migration[5.2]
  def change
    enable_extension 'hstore'
    add_column :station_details, :jita_distance, :integer, limit: 2
    add_column :station_details, :industry_costs_indices, :hstore
  end
end
