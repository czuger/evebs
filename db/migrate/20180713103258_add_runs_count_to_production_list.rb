class AddRunsCountToProductionList < ActiveRecord::Migration[5.2]
  def change
    add_column :production_lists, :runs_count, :integer, limit: 2
  end
end
