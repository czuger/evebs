class RemoveQuantityToProduceFromProductionList < ActiveRecord::Migration[5.2]
  def up
    drop_view :component_to_buys, revert_to_version: 10
    remove_column :production_lists, :quantity_to_produce, :bigint
    change_column :production_lists, :runs_count, :integer, limit: 2
  end

  def down
    add_column :production_lists, :quantity_to_produce, :bigint
    change_column :production_lists, :runs_count, :bigint, null: true
    create_view :component_to_buys
  end

end
