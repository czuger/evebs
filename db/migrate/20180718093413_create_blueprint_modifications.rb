class CreateBlueprintModifications < ActiveRecord::Migration[5.2]
  def change
    create_table :blueprint_modifications do |t|
      t.references :user, foreign_key: true, null: false, index: false
      t.references :blueprint, foreign_key: true, null: false, index: false
      t.float :percent_modification_value, null: false
      t.boolean :touched, null: false, default: false

      t.timestamps
    end

    add_index :blueprint_modifications, [ :user_id, :blueprint_id ], unique: true
  end
end
