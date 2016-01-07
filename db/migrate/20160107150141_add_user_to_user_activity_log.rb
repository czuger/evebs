class AddUserToUserActivityLog < ActiveRecord::Migration
  def change
    add_column :user_activity_logs, :user, :string
  end
end
