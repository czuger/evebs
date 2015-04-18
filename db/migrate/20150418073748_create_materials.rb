class CreateMaterials < ActiveRecord::Migration
  def change
    create_table :materials do |t|
      t.references :blueprint, index: true
      t.references :component, index: true
      t.integer :required_qtt

      t.timestamps
    end
  end
end
