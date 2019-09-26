class AddInitializationFinalizedToUser < ActiveRecord::Migration[5.2]
  def change
    add_column :users, :initialization_finalized, :boolean, null: false, default: false
  end
end
