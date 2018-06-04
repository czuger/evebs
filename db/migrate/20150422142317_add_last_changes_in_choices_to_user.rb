class AddLastChangesInChoicesToUser < ActiveRecord::Migration[4.2]
  def change
    add_column :users, :last_changes_in_choices, :datetime
  end
end
