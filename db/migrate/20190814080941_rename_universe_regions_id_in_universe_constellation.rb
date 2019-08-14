class RenameUniverseRegionsIdInUniverseConstellation < ActiveRecord::Migration[5.2]
  def change
    rename_column :universe_constellations, :universe_regions_id, :universe_region_id
  end
end
