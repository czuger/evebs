class UpdateStructures < ActiveRecord::Migration[5.2]
  def change
    remove_column :structures, :trade_hub_id, :bigint;

    add_reference :structures, :universe_system, foreign_key: true;
    add_column :structures, :orders_count_pages, :integer;

    add_index :structures, :cpp_structure_id, unique: true
  end
end
