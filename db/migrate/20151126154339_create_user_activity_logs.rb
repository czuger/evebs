class CreateUserActivityLogs < ActiveRecord::Migration
  def change
    create_table :user_activity_logs do |t|
      t.string :ip
      t.string :action

      t.timestamps null: false
    end
  end
end
