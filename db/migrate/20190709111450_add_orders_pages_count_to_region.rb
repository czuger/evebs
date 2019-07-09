class AddOrdersPagesCountToRegion < ActiveRecord::Migration[5.2]
  def change
    add_column :regions, :orders_pages_count, :integer, null: false, default: 0
  end
end
