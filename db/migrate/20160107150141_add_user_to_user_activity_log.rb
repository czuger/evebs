class AddUserToUserActivityLog < ActiveRecord::Migration[4.2]
  def change
    add_column :user_activity_logs, :user, :string
  end
end
