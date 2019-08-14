class AddOrdersPagesCountToUniverseRegion < ActiveRecord::Migration[5.2]
  def change
    add_column :universe_regions, :orders_pages_count, :integer, null: false, default: 0
    remove_column :regions, :orders_pages_count, :integer
  end
end
