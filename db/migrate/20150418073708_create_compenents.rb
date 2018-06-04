class CreateCompenents < ActiveRecord::Migration[4.2]
  def change
    create_table :compenents do |t|
      t.integer :cpp_eve_item_id
      t.string :name
      t.float :cost

      t.timestamps
    end
  end
end
