class AddNameLowcaseToEveItem < ActiveRecord::Migration[4.2]
  def change
    add_column :eve_items, :name_lowcase, :string
  end
end
