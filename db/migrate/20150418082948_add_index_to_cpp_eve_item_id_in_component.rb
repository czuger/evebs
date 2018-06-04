class AddIndexToCppEveItemIdInComponent < ActiveRecord::Migration[4.2]
  def change
    add_index :compenents, :cpp_eve_item_id
  end
end
