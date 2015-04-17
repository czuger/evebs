class AddCostToEveItem < ActiveRecord::Migration
  def change
    add_column :eve_items, :cost, :float
  end
end
