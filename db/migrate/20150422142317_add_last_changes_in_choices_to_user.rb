class AddLastChangesInChoicesToUser < ActiveRecord::Migration
  def change
    add_column :users, :last_changes_in_choices, :datetime
  end
end
