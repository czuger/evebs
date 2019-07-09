class ChangeStationDetailsIndustryCostsIndices < ActiveRecord::Migration[5.2]
  def change
    remove_column :station_details, :industry_costs_indices
    add_column :station_details, :industry_costs_indices, :jsonb
  end
end
