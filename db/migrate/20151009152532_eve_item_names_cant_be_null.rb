class EveItemNamesCantBeNull < ActiveRecord::Migration
  def change
    change_column_null :eve_items, :name, false
  end
end
