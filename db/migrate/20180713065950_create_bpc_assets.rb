class CreateBpcAssets < ActiveRecord::Migration[5.2]
  def change
    create_table :bpc_assets do |t|
      t.references :character,foreign_key: true,  null: false
      t.references :blueprint_component, foreign_key: true, null: false
      t.references :station_detail, foreign_key: true
      t.bigint :quantity, null: false
      t.boolean :touched, null: false, default: false

      t.timestamps
    end
  end
end
