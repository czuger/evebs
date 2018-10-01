class CreateLastUpdates < ActiveRecord::Migration[5.2]
  def change
    create_table :last_updates do |t|
      t.string :update_type, null: false
      t.datetime :updated_at, null: false

      # t.timestamps
    end
  end
end
