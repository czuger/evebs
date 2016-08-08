class RemoveEveClient < ActiveRecord::Migration
  def change
    drop_table :eve_clients
  end
end
