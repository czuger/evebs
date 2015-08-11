class CreateEveClients < ActiveRecord::Migration
  def change
    create_table :eve_clients do |t|
      t.integer :cpp_client_id, null: false
      t.string :name, null: false

      t.timestamps
    end
    add_index :eve_clients, :cpp_client_id, unique: true
  end
end
