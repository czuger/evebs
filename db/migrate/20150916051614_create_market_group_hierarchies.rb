class CreateMarketGroupHierarchies < ActiveRecord::Migration[4.2]
  def change
    create_table :market_group_hierarchies, id: false do |t|
      t.integer :ancestor_id, null: false
      t.integer :descendant_id, null: false
      t.integer :generations, null: false
    end

    add_index :market_group_hierarchies, [:ancestor_id, :descendant_id, :generations],
      unique: true,
      name: "market_group_anc_desc_idx"

    add_index :market_group_hierarchies, [:descendant_id],
      name: "market_group_desc_idx"
  end
end
