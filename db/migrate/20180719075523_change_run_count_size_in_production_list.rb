class ChangeRunCountSizeInProductionList < ActiveRecord::Migration[5.2]
  def change
    drop_view :component_to_buys
    change_column :production_lists, :runs_count, :bigint
  end
end
