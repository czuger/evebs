class RemoveEditFromUser < ActiveRecord::Migration
  def change
    remove_column :users, :edit, :string
  end
end
