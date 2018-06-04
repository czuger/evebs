class AddCostToEveItem < ActiveRecord::Migration[4.2]
  def change
    add_column :eve_items, :cost, :float
  end
end
