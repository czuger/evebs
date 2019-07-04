class CreateUniverseSystems < ActiveRecord::Migration[5.2]
  def change
    create_table :universe_systems do |t|
      t.integer :cpp_system_id, null: false
      t.string :name, null: false
      t.boolean :trade_hub, null: false, default: false, index: true
      t.integer :cpp_constellation_id, null: false
      t.integer :cpp_star_id, null: false
      t.string :security_class
      t.float :security_status, null: false
      t.integer :stations_ids, null: false, array: true, default: []

      t.integer :kill_stats_last_week, null: false, default: 0
      t.integer :kill_stats_last_month, null: false, default: 0

      t.timestamps
    end
  end
end
