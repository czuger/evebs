class CreateCrontabs < ActiveRecord::Migration[5.2]
  def change
    create_table :crontabs do |t|
      t.string :cron_name, null: false
      t.boolean :status, null: false, default: false

      t.timestamps
    end
  end
end
