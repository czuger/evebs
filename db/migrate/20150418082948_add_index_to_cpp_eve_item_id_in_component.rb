class AddIndexToCppEveItemIdInComponent < ActiveRecord::Migration
  def change
    add_index :compenents, :cpp_eve_item_id
  end
end
