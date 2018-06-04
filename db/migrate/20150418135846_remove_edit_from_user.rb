class RemoveEditFromUser < ActiveRecord::Migration[4.2]
  def change
    remove_column :users, :edit, :string
  end
end
