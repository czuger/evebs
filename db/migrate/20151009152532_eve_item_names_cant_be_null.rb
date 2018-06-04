class EveItemNamesCantBeNull < ActiveRecord::Migration[4.2]
  def change
    change_column_null :eve_items, :name, false
  end
end
