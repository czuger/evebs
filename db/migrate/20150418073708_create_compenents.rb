class CreateCompenents < ActiveRecord::Migration
  def change
    create_table :compenents do |t|
      t.integer :cpp_eve_item_id
      t.string :name
      t.float :cost

      t.timestamps
    end
  end
end
