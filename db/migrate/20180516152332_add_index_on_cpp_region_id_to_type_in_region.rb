class AddIndexOnCppRegionIdToTypeInRegion < ActiveRecord::Migration[5.2]
  def change
    add_index :type_in_regions, :cpp_region_id
  end
end
