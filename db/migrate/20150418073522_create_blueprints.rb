class CreateBlueprints < ActiveRecord::Migration
  def change
    create_table :blueprints do |t|
      t.references :eve_item, index: true
      t.integer :nb_runs
      t.integer :prod_qtt

      t.timestamps
    end
  end
end
