class RemoveQuantityToProduceFromProductionList < ActiveRecord::Migration[5.2]
  def up
    drop_view :components_to_buys_details, revert_to_version: 10
    remove_column :production_lists, :quantity_to_produce, :bigint
    change_column :production_lists, :runs_count, :integer, limit: 2, null: false
  end

  def down
    add_column :production_lists, :quantity_to_produce, :bigint
    change_column :production_lists, :runs_count, :bigint, null: true
    create_view :components_to_buys_details
  end

end
