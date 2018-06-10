class CreateStructures < ActiveRecord::Migration[5.2]
  def change
    create_table :structures do |t|
      t.bigint :cpp_structure_id
      t.references :trade_hub, foreign_key: true, index: true

      t.timestamps
    end
  end
end
