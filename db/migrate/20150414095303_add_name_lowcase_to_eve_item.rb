class AddNameLowcaseToEveItem < ActiveRecord::Migration
  def change
    add_column :eve_items, :name_lowcase, :string
  end
end
