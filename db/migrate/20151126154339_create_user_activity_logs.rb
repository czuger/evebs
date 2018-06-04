class CreateUserActivityLogs < ActiveRecord::Migration[4.2]
  def change
    create_table :user_activity_logs do |t|
      t.string :ip
      t.string :action

      t.timestamps null: false
    end
  end
end
