class RemoveEveClient < ActiveRecord::Migration[4.2]
  def change
    drop_table :eve_clients
  end
end
